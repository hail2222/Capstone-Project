from fastapi import APIRouter
from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import datetime

from ..auth.authenticate import authenticate
from ..db.connection import get_db
from ..schemas.schemas import TokenResponse, UserSchema, EventSchema, GroupSchema, MeetingSchema
from ..cruds.cruds import get_login, signin, signup, get_all_events,\
    event_register, event_remove, event_update, get_all_friends, \
    friend_register, group_register, group_update, member_register, \
    meeting_register, meeting_remove, meeting_update, get_all_meetings, \
    google_event_register
router = APIRouter()

# @router.get("/{id}")
# async def load_user(id: str, db: Session = Depends(get_db)):
#     user = db.query(User).filter(User.id == id).first()
#     if not user:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No user")
#     return {"pw": user.pw}

@router.get("/login")
async def login(user: str = Depends(authenticate)):
    login_success = await get_login(user)
    return login_success

@router.post("/signin", response_model=TokenResponse)
async def signin_user(user: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    get_token = await signin(user, db)
    return get_token

@router.post("/signup")
async def signup_user(user: UserSchema, db: Session = Depends(get_db)):
    register_success = await signup(user, db)
    return register_success

@router.get("/event")    
async def get_event(date: datetime.date, user: str = Depends(authenticate), db: Session = Depends(get_db)):
    event_list = await get_all_events(date, user, db)
    return event_list

@router.post("/event")
async def add_event(event: EventSchema, user: str = Depends(authenticate), db: Session = Depends(get_db)):
    register_success = await event_register(event, user, db)
    return register_success

@router.delete("/event")    
async def del_event(cid: int, user: str = Depends(authenticate), db: Session = Depends(get_db)):
    remove_success = await event_remove(cid, user, db)
    return remove_success

@router.put("/event")
async def update_event(cid: int, event: EventSchema, user: str = Depends(authenticate), db: Session = Depends(get_db)):
    update_success = await event_update(cid, event, user, db)
    return update_success


@router.get("/friend")
async def get_friend(user: str = Depends(authenticate), db: Session = Depends(get_db)):
    friend_list = await get_all_friends(user, db)
    return friend_list

@router.post("/friend")
async def add_friend(fid: str, user: str = Depends(authenticate), db: Session = Depends(get_db)):
    register_success = await friend_register(fid, user, db)
    return register_success

@router.post("/group")
async def add_group(gname: str, user: str = Depends(authenticate), db: Session = Depends(get_db)):
    register_success = await group_register(gname, user, db)
    return register_success

@router.put("/group")
async def update_group(gid: int, group: GroupSchema, db: Session = Depends(get_db)):
    update_success = await group_update(gid, group, db)
    return update_success


@router.post("/member")
async def add_member(gid: int, member: str, user: str = Depends(authenticate), db: Session = Depends(get_db)):
    register_success = await member_register(gid, member, user, db)
    return register_success


@router.get("/meeting")    
async def get_meeting(gid: int, db: Session = Depends(get_db)):
    meeting_list = await get_all_meetings(gid, db)
    return meeting_list

@router.post("/meeting")
async def add_meeting(gid: int, db: Session = Depends(get_db)):
    register_success = await meeting_register(gid, db)
    return register_success

@router.put("/meeting")
async def update_event(meetid: int, meeting: MeetingSchema, db: Session = Depends(get_db)):
    update_success = await meeting_update(meetid, meeting, db)
    return update_success

@router.delete("/meeting")    
async def del_meeting(meetid: int, db: Session = Depends(get_db)):
    remove_success = await meeting_remove(meetid, db)
    return remove_success

# google calendar 연동
@router.post("/google")
async def add_google_events(user: str = Depends(authenticate), db: Session = Depends(get_db)):
    register_success = await google_event_register(user, db)
    return register_success