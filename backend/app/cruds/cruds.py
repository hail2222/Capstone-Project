from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from sqlalchemy import func, or_, and_
from datetime import datetime, timedelta

from ..auth.jwt_handler import create_access_token
from ..models.models import User, Event, Friend, FriendRequest, Group, Member, Meeting, GroupEvent, Invited, Favorite
from ..auth.hash_password import HashPassword
from ..schemas.schemas import UserSchema, EventSchema, GroupSchema, MeetingSchema, FriendSchema
from ..googlecal.cal_func import get_event
import random

hash_password = HashPassword()

async def get_login(user: str):
    return {"success": True}

async def signin(user: OAuth2PasswordRequestForm, db: Session):
    user_exist = db.query(User).filter(User.id == user.username).first()
    if not user_exist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User doesn't exist")
    if hash_password.verify_hash(user.password, user_exist.pw):
        access_token = create_access_token(user_exist.id)
        return {
            "access_token": access_token,
            "token_type": "Bearer",
            "username": user_exist.name
        }
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid details passed")

async def signup(user: UserSchema, db: Session):
    user_exist = db.query(User).filter(User.id == user.id).first()
    if user_exist:
        raise HTTPException(status_code=401, detail="Existed user")
    user.pw = hash_password.create_hash(user.pw)
    db_user = User(id=user.id, pw=user.pw, name=user.name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"msg": "User created successfully."}

# async def get_all_events(date: datetime.date, user: str, db: Session):
#     return db.query(Event).filter(Event.uid == user, func.date(Event.sdatetime) <= date, date <= func.date(Event.edatetime)).all()

async def get_all_events(user: str, db: Session):
    return db.query(Event).filter(Event.uid == user).all()

def genPass():
    alphabet="abcdefghijklmnopqrstuvwxyz0123456789"
    weekly_word=""
    for i in range(6):
        index=random.randrange(len(alphabet))
        weekly_word=weekly_word+alphabet[index]
    return weekly_word

async def event_register(event: EventSchema, user: str, db: Session):
    if event.edatetime <= event.sdatetime:
        return {"msg": "invalid event."}
    event_exist = db.query(Event).filter(Event.uid == user,
    or_(
        and_((Event.sdatetime <= event.sdatetime), (event.sdatetime < Event.edatetime)),
        and_((Event.sdatetime < event.edatetime), (event.edatetime <= Event.edatetime)),
        and_((event.sdatetime <= Event.sdatetime), (Event.sdatetime < event.edatetime)),
        and_((event.sdatetime < Event.edatetime), (Event.edatetime <= event.edatetime))
        )
    ).all()
    if event_exist:
        return {"msg": "event exist."}    
    # enddate가 null이 아니면 enddate까지 일주일마다 반복
    if event.enddate:
        if event.edatetime.date() > event.enddate:
            return {"msg": "invalid event."}
        else:
            weekly_id=genPass()
            while event.edatetime.date()<=event.enddate:
                db_event = Event(uid=user, cname=event.cname, visibility=event.visibility, \
                    sdatetime=event.sdatetime, edatetime=event.edatetime, weekly=weekly_id, enddate=event.enddate)
                db.add(db_event)
                db.commit()
                db.refresh(db_event)
                event.sdatetime+=timedelta(weeks=1)
                event.edatetime+=timedelta(weeks=1)
    # enddate가 null이면 반복 x
    else:       
        db_event = Event(uid=user, cname=event.cname, visibility=event.visibility, \
            sdatetime=event.sdatetime, edatetime=event.edatetime, weekly=event.weekly, enddate=event.enddate)
        db.add(db_event)
        db.commit()
        db.refresh(db_event)
    calendar_success = await groupcal_register(db_event.cid, user, db)
    return {"msg": "event added successfully."}
        

async def event_remove(cid: int, deleteall: bool, user: str, db: Session):
    db_event = db.query(Event).filter(Event.uid == user, Event.cid == cid).first()
    if not db_event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event doesn't exist")
    db.delete(db_event)
    db.commit()
    weekly_id=db_event.weekly
    
    if deleteall==True and weekly_id!="0":        
        while True:
            db_event = db.query(Event).filter(Event.uid == user, Event.weekly == weekly_id).first()
            if not db_event:
                break
            db.delete(db_event)
            db.commit()
    calendar_success = await groupcal_remove(cid, db)
    return {"msg": "event deleted successfully."}    

async def event_update(cid: int, event: EventSchema, user: str, db: Session):
    db_event = db.query(Event).filter(Event.uid == user, Event.cid == cid).first()
    if not db_event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event doesn't exist")
    db_event.cname = event.cname
    db_event.visibility = event.visibility
    db_event.sdatetime = event.sdatetime
    db_event.edatetime = event.edatetime
    db.add(db_event)
    db.commit()
    calendar_success = await groupcal_update(cid, event, db)
    return {"msg": "event updated successfully."}


async def get_all_friends(user: str, db: Session):
    select = db.query(User).join(Friend, Friend.fid == User.id).filter(Friend.uid == user).all()
    friendList = []
    for i in select:
        friendList.append({"id": i.id, "name": i.name})
    return friendList

async def friend_register(friend: FriendSchema, user: str, db: Session):
    friend_user_exist = db.query(User).filter(User.id == friend.fid).first()
    if not friend_user_exist:
        raise HTTPException(status_code=404, detail="There is no user")
    already_friend = db.query(Friend).filter(Friend.uid == user, Friend.fid == friend.fid).first()
    if already_friend:
        raise HTTPException(status_code=401, detail="already friend")
    db_friendship_1 = Friend(uid=user, fid=friend.fid)
    db_friendship_2 = Friend(uid=friend.fid, fid=user)
    db.add(db_friendship_1)
    db.add(db_friendship_2)
    db.commit()
    db.refresh(db_friendship_1)
    db.refresh(db_friendship_2)
    return {"msg": "friend added successfully."}

async def friend_remove(friend: FriendSchema, user: str, db: Session):
    db_friendship1 = db.query(Friend).filter(Friend.uid == user, Friend.fid == friend.fid).first()
    if not db_friendship1:
        raise HTTPException(status_code=404, detail="There is no friend")
    db_friendship2 = db.query(Friend).filter(Friend.uid == friend.fid, Friend.fid == user).first()
    db.delete(db_friendship1)
    db.delete(db_friendship2)
    db.commit()
    return {"msg": "friend deleted successfully."}

async def get_all_requests(user: str, db: Session):
    return db.query(FriendRequest).filter(FriendRequest.fid == user).all()

async def friend_request(friend: FriendSchema, user: str, db: Session):
    friend_user_exist = db.query(User).filter(User.id == friend.fid).first()
    if not friend_user_exist:
        raise HTTPException(status_code=404, detail="There is no user")
    already_friend = db.query(Friend).filter(Friend.uid == user, Friend.fid == friend.fid).first()
    if already_friend:
        raise HTTPException(status_code=401, detail="already friend")

    friend_request_exist = db.query(FriendRequest).filter(or_(FriendRequest.uid == user, FriendRequest.fid == user)).all()
    if friend_request_exist:
        raise HTTPException(status_code=401, detail="already request")

    db_friendrequest = FriendRequest(uid=user, fid=friend.fid)
    db.add(db_friendrequest)
    db.commit()
    db.refresh(db_friendrequest)
    return {"msg": "send friend request successfully."}

async def request_remove(friend: FriendSchema, user: str, db: Session):
    friend_request_exist = db.query(FriendRequest).filter(FriendRequest.uid == user, FriendRequest.fid == friend.fid).first()
    if not friend_request_exist:
        raise HTTPException(status_code=404, detail="There is no request")

    db.delete(friend_request_exist)
    db.commit()
    return {"msg": "delete friend request successfully."}

async def friend_accept(friend: FriendSchema, user: str, db: Session):
    friend_request_exist = db.query(FriendRequest).filter(FriendRequest.uid == friend.fid, FriendRequest.fid == user).first()
    if not friend_request_exist:
        raise HTTPException(status_code=404, detail="There is no request")

    db_friendship_1 = Friend(uid=user, fid=friend.fid)
    db_friendship_2 = Friend(uid=friend.fid, fid=user)
    db.add(db_friendship_1)
    db.add(db_friendship_2)
    db.delete(friend_request_exist)
    db.commit()
    db.refresh(db_friendship_1)
    db.refresh(db_friendship_2)
    return {"msg": "friend added successfully."}

async def accept_remove(friend: FriendSchema, user: str, db: Session):
    friend_request_exist = db.query(FriendRequest).filter(FriendRequest.uid == friend.fid, FriendRequest.fid == user).first()
    if not friend_request_exist:
        raise HTTPException(status_code=404, detail="There is no accept")

    db.delete(friend_request_exist)
    db.commit()
    return {"msg": "reject accept successfully."}

async def group_register(group: GroupSchema, user: str, db: Session):
    db_group = Group(gname=group.gname, admin=user)
    db.add(db_group)
    db.commit()
    db.refresh(db_group)
    register_success = await member_register2(db_group.gid, user, user, db)
    return {"msg": "group added successfully."}

# 그룹명 수정
async def group_update(gid: int, group: GroupSchema, db: Session):
    db_group = db.query(Group).filter(Group.gid == gid).first()
    if not db_group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group doesn't exist")
    db_group.gname = group.gname
    db.add(db_group)
    db.commit()
    db.refresh(db_group)
    return {"msg": "group name updated successfully."}

async def group_leave(gid: int, user: str, db: Session):
    db_group = db.query(Group).filter(Group.gid == gid).first()
    if not db_group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group doesn't exist")
    db_member = db.query(Member).filter(Member.gid == gid, Member.uid == user).first()
    if not db_member:
        raise HTTPException(status_code=401, detail="Not group member")
    db.delete(db_member)
    db.commit()
    
    db_favorite = db.query(Favorite).filter(Favorite.gid == gid, Favorite.uid == user).first()
    if not db_favorite:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Favorite group doesn't exist")
    db.delete(db_favorite)
    db.commit()
    
    db_event = db.query(Event).filter(Event.uid == user).all()
    for x in db_event:
        db_delete = db.query(GroupEvent).filter(GroupEvent.gid == gid, GroupEvent.ccid == x.cid).first()
        db.delete(db_delete)
        db.commit()
    return {"msg": "group member deleted successfully."}

async def invited_register(gid: int, uid: str, user: str, db: Session):
    db_user = db.query(User).filter(User.id == uid).first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User doesn't exist")
    already_invited = db.query(Invited).filter(Invited.uid == uid, Invited.gid == gid).first()
    if already_invited:
        raise HTTPException(status_code=401, detail="already invited")
    already_member = db.query(Member).filter(Member.gid == gid, Member.uid == uid).first()
    if already_member:
        raise HTTPException(status_code=401, detail="already member")
    db_group = Invited(gid=gid, uid=uid)
    db.add(db_group)
    db.commit()
    db.refresh(db_group)
    return {"msg": "invited added successfully."}

async def invited_delete(gid: int, user: str, db: Session):
    already_invited = db.query(Invited).filter(Invited.uid == user, Invited.gid == gid).first()
    if not already_invited:
        raise HTTPException(status_code=401, detail="not already invited")
    
    db.delete(already_invited)
    db.commit()
    return {"msg": "invited deleted successfully."}

    
async def get_all_meetings(gid: int, db: Session):
    return db.query(Meeting).filter(Meeting.gid == gid).all()

async def meeting_register(gid: int, db: Session):
    db_meeting = Meeting(gid=gid)
    db.add(db_meeting)
    db.commit()
    db.refresh(db_meeting)
    return {"msg": "meeting added successfully."}

async def meeting_update(meetid: int, meeting: MeetingSchema, db: Session):
    db_meeting = db.query(Meeting).filter(Meeting.meetid == meetid).first()
    if not db_meeting:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meeting doesn't exist")
    db_meeting.title = meeting.title
    db_meeting.sdatetime = meeting.sdatetime
    db_meeting.edatetime = meeting.edatetime
    db_meeting.location = meeting.location
    db_meeting.memo = meeting.memo
    db.add(db_meeting)
    db.commit()
    return {"msg": "meeting info updated successfully."}

async def meeting_remove(meetid: int, db: Session):
    db_meeting = db.query(Meeting).filter(Meeting.meetid == meetid).first()
    if not db_meeting:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meeting doesn't exist")
    db.delete(db_meeting)
    db.commit()
    return {"msg": "meeting deleted successfully."}

async def get_all_members(gid: int, user: str, db: Session):
    return db.query(Member.uid).filter(Member.gid == gid).all()

async def member_register(gid: int, user: str, db: Session):
    db_user = db.query(User).filter(User.id == user).first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User doesn't exist")
    already_member = db.query(Member).filter(Member.gid == gid, Member.uid == user).first()
    if already_member:
        raise HTTPException(status_code=401, detail="already member")
    already_invited = db.query(Invited).filter(Invited.uid == user, Invited.gid == gid).first()
    if not already_invited:
        raise HTTPException(status_code=401, detail="not already invited")
    db_member = Member(gid=gid, uid=user)
    db.add(db_member)
    db.delete(already_invited)
    db.commit()
    db.refresh(db_member)
    calendar_success = await groupcal_register2(gid, user, db)
    return {"msg": "member added successfully."}

async def member_register2(gid: int, member: str, user: str, db: Session):
    db_user = db.query(User).filter(User.id == member).first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User doesn't exist")
    already_member = db.query(Member).filter(Member.gid == gid, Member.uid == member).first()
    if already_member:
        raise HTTPException(status_code=401, detail="already member")
    db_member = Member(gid=gid, uid=member)
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    calendar_success = await groupcal_register2(gid, member, db)
    return {"msg": "member added successfully."}

# 멤버인 상태에서 개인 캘린더 추가하면 반영
async def groupcal_register(ccid: int, member: str, db: Session):
    db_member = db.query(Member).filter(Member.uid == member).all()
    for x in db_member:
        db_exist = db.query(Event).filter(Event.uid == member, Event.cid == ccid).first()
        if not db_exist:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event doesn't exist") 
        db_event = GroupEvent(gid=x.gid, ccid=db_exist.cid, cname=db_exist.cname, \
            sdatetime=db_exist.sdatetime, edatetime=db_exist.edatetime, visibility=db_exist.visibility)
        db.add(db_event)
        db.commit()
    return {"msg": "group calendar added successfully."}

# 멤버 등록시 그룹캘린더에 일정 추가
async def groupcal_register2(gid: int, member: str, db: Session):
    db_group = db.query(Group).filter(Group.gid == gid).first()
    if not db_group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group doesn't exist") 
    db_allevent = db.query(Event).filter(Event.uid == member).all()
    for x in db_allevent:
        db_event = GroupEvent(gid=gid, ccid=x.cid, cname=x.cname, \
            sdatetime=x.sdatetime, edatetime=x.edatetime, visibility=x.visibility)
        db.add(db_event)
        db.commit()
    return {"msg": "user events added to group calendar successfully."}

async def groupcal_update(ccid: int, event: EventSchema, db: Session):
    db_event = db.query(GroupEvent).filter(GroupEvent.ccid == ccid).all()
    if not db_event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meeting doesn't exist")
    for x in db_event:
        x.cname = event.cname
        x.sdatetime = event.sdatetime
        x.edatetime = event.edatetime
        x.visibility = event.visibility
        db.add(x)
        db.commit()
    return {"msg": "meeting info updated successfully."}

async def groupcal_remove(ccid: int, db: Session):
    db_event = db.query(GroupEvent).filter(GroupEvent.ccid == ccid).all()
    if not db_event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meeting doesn't exist")
    for x in db_event:
        db.delete(x)
        db.commit()
    return {"msg": "meeting deleted successfully."}

async def get_all_groupcal(gid: int, user: str, db: Session):
    return db.query(GroupEvent).filter(GroupEvent.gid == gid).all()

async def google_event_register(user: str, db: Session):
    google=get_event()
    # print(google)
    if google==None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Google event doesn't exist")
    for event in google:
        sdt=event[0]
        edt=event[1]
        cn=event[2]
        vsb=event[3]
        event_exist = db.query(Event).filter(Event.uid == user,
        or_(
            and_((Event.sdatetime <= sdt), (sdt < Event.edatetime)),
            and_((Event.sdatetime < edt), (edt <= Event.edatetime)),
            and_((sdt <= Event.sdatetime), (Event.sdatetime < edt)),
            and_((sdt< Event.edatetime), (Event.edatetime <= edt))
            )
        ).all()
        
        if event_exist:
            continue
        else:
            db_event = Event(uid=user, cname=cn, visibility=vsb, sdatetime=sdt, edatetime=edt, weekly="0", enddate=None)
            db.add(db_event)
            db.commit()
            db.refresh(db_event)
    return {"msg": "google calendar events added successfully."}

async def get_my_group(user: str, db: Session):
    db_group = db.query(Group).filter(Group.gid == Member.gid, Member.uid == user).all()
    if not db_group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group doesn't exist")
    return db_group

async def get_my_invited(user: str, db: Session):
    db_invited = db.query(Invited).filter(Invited.uid == user).all()
    if not db_invited:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invited list doesn't exist")
    return db_invited


from fastapi import Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

templates=Jinja2Templates(directory='./app/kakaoshare')
async def send_kakao(req: Request, gid: int, user: str, db: Session):
    db_group = db.query(Group).filter(Group.gid == gid).first()
    if not db_group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group doesn't exist")
    return templates.TemplateResponse("kakao_share.html",
                                      {"request": req,
                                       "groupname": db_group.gname,
                                       "gid": gid,
                                       "username": user})
    # return RedirectResponse("/", status_code=302)

async def get_weekly_groupcal(gid: int, start_date: datetime, end_date: datetime, db: Session):
    db_event = db.query(GroupEvent).filter(
        GroupEvent.gid == gid, 
        GroupEvent.sdatetime <= end_date + timedelta(days=1),
        GroupEvent.edatetime >= start_date
    ).all()
    if not db_event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group calendar doesn't exist")
    return db_event

# get group info by gid
async def get_groupinfo(gid: int, db: Session):
    db_group = db.query(Group).filter(Group.gid == gid).first()
    if not db_group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group doesn't exist")
    return db_group


async def favorite_group_register(gid: int, user: str, db: Session):
    db_group = db.query(Group).filter(Group.gid == gid).first()
    if not db_group:
        raise HTTPException(status_code=401, detail="group doesn't exist")
    db_member = db.query(Member).filter(Member.gid == gid, Member.uid == user).first()
    if not db_member:
        raise HTTPException(status_code=401, detail="not group member")
    db_group = db.query(Group).filter(Group.gid == gid).first()
    db_favorite = Favorite(uid=user, gid=gid, gname=db_group.gname)
    db.add(db_favorite)
    db.commit()
    db.refresh(db_favorite)
    return {"msg": "favorite group added successfully."}

async def favorite_group_get(user: str, db: Session):
    db_favorite = db.query(Favorite).filter(Favorite.uid == user).all()
    if not db_favorite:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Favorite list doesn't exist")
    return db_favorite

async def favorite_group_delete(gid: int, user: str, db: Session):
    db_favorite = db.query(Favorite).filter(Favorite.gid == gid, Favorite.uid == user).first()
    if not db_favorite:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Favorite group doesn't exist")
    db.delete(db_favorite)
    db.commit()
    return {"msg": "favorite deleted successfully."}