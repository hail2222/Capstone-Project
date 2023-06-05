import React, { useState } from "react";
import { useRef, useEffect } from "react";
import { useParams, useHistory, useLocation } from "react-router-dom";
import { Modal } from "react-bootstrap";
import Main from "./group-timetable/Main";
import { Form } from "react-bootstrap";
import Timeslot from "./group-timetable/components/Timeslot";
import TimeTable from "./group-timetable/components/Time-table";
import AdminBox from "./group-timetable/components/AdminBox";
import NonAdminBox from "./group-timetable/components/NonAdminBox";
import GroupCalContext from "./GroupCalContext";
import { Bar, Doughnut } from "react-chartjs-2";
import axios from "axios";

const realURL = "https://port-0-timecodi-416cq2mlg8dr0qo.sel3.cloudtype.app";
const localURL = "https://127.0.0.1:8000";
const url = realURL;

function Group() {
  let location = useLocation();
  let currentPath = location.pathname;
  let gid = parseInt(currentPath.split("/").pop(), 10);
  const [gname, setGname] = useState("");
  const [admin, setAdmin] = useState("");

  const [groupCal, setGroupCal] = useState(null);
  const fetchGroupCal = async () => {
    const data = localStorage.getItem("groupWeeklyCal");
    if (data) {
      setGroupCal(JSON.parse(data));
    }
  };

  let start_date = new Date();
  let end_date = new Date();

  function getStartDate() {
    if (groupCal) {
      const groupCal_dict = groupCal[0];
      const first_list = groupCal_dict["first_list"];
      const first_key = Object.keys(first_list)[0]; // 1st list의 가능한 인원수
      const first_value = first_list[first_key];
      const first_date = first_value[0]; // 1st list의 가능한 날짜
      let dateStr = first_date[0]; // string 형태의 날짜
      let date = new Date(dateStr);
      let dayOfWeek = date.getUTCDay();
      let diffToSun = dayOfWeek;
      let diffToSat = 6 - dayOfWeek;
      let startDate = new Date(date);
      startDate.setDate(date.getDate() - diffToSun);
      let endDate = new Date(date);
      endDate.setDate(date.getDate() + diffToSat);
      start_date = startDate.toISOString().substring(0, 10);
      end_date = endDate.toISOString().substring(0, 10);
    }
    console.log("start_date", start_date);
    console.log("end_date", end_date);
  }

  const getGroupInfo = () => {
    console.log("get group info by gid");
    axios
      .get(`${url}/groupinfo?gid=${gid}`, {
        headers: {
          Authorization: localStorage.getItem("token"),
        },
      })
      .then((res) => {
        console.log(res.data);
        setGname(res.data.gname);
        setAdmin(res.data.admin);
      })
      .catch((err) => {
        console.log("get group info by id");
        console.log(err);
      });
  };
  const [oo, setOO] = useState(false);
  const history = useHistory();

  axios
    .get("https://port-0-timecodi-416cq2mlg8dr0qo.sel3.cloudtype.app/login", {
      headers: {
        Authorization: localStorage.getItem("token"),
      },
    })
    .then((response) => {
      if (response.data.success == true) {
        // alert("good");
      }
    })
    .catch((err) => {
      setOO(true);
    });

  useEffect(() => {
    if (oo) {
      history.push("/user-pages/login-1");
      // alert("please login");
    }
  }, [oo]);

  // const { gid } = useParams();

  const [show, setShow] = useState(false);

  const handleShow = () => setShow(true);
  const chartRef = useRef(null);
  const [addShow, setAddShow] = useState(false);
  const addClose = () => setAddShow(!addShow);

  const [addFriend, setFriend] = useState(false);
  const friendClose = () => setFriend(!addFriend);

  const [members, setMembers] = useState([]);

  const getMembers = () => {
    axios
      .get(
        "https://port-0-timecodi-416cq2mlg8dr0qo.sel3.cloudtype.app/member",
        {
          headers: {
            Authorization: localStorage.getItem("token"),
          },
          params: {
            gid: gid,
          },
        }
      )
      .then((response) => {
        let memberList = [];
        response.data.forEach((rel, index) => {
          memberList.push({ id: rel.id, name: rel.name });
        });
        setMembers(memberList);
      })
      .catch((err) => {
        console.log(err);
      });
  };

  const [isAdmin, setIsAdmin] = useState(false);

  const getAdmin = () => {
    axios
      .get("https://port-0-timecodi-416cq2mlg8dr0qo.sel3.cloudtype.app/admin", {
        headers: {
          Authorization: localStorage.getItem("token"),
        },
        params: {
          gid: gid,
        },
      })
      .then((response) => {
        setIsAdmin(response.data);
      })
      .catch((err) => {
        console.log(err);
      });
  };

  useEffect(() => {
    getGroupInfo();
    getMembers();
    getAdmin();
  }, []);

  const inviteMember = (userId) => {
    const data = { gid: gid, uid: userId };

    axios
      .post(
        "https://port-0-timecodi-416cq2mlg8dr0qo.sel3.cloudtype.app/invited",
        data,
        {
          headers: {
            Authorization: localStorage.getItem("token"),
          },
        }
      )
      .then((response) => {
        addClose();
        alert("invite success!");
      })
      .catch((err) => {
        console.log(err);
      });
  };
  // let members = ["David Grey", "Stella Johnson", "Marina Michel", "John Doe"];
  // let [memberList] = useState(members);

  let [isVoteActive] = useState(true);
  let [options, setOptions] = useState([
    {
      id: 1,
      content: "2023-04-25 14:00 ~ 16:00",
      checked: false,
    },
    {
      id: 2,
      content: "2023-04-25 14:30 ~ 16:30",
      checked: false,
    },
    {
      id: 3,
      content: "2023-04-25 15:00 ~ 17:00",
      checked: false,
    },
    {
      id: 4,
      content: "2023-04-26 13:00 ~ 15:00",
      checked: false,
    },
    {
      id: 5,
      content: "2023-04-25 14:00 ~ 16:00",
      checked: false,
    },
    {
      id: 6,
      content: "2023-04-25 14:30 ~ 16:30",
      checked: false,
    },
    {
      id: 7,
      content: "2023-04-25 15:00 ~ 17:00",
      checked: false,
    },
    {
      id: 8,
      content: "2023-04-26 13:00 ~ 15:00",
      checked: false,
    },
  ]);
  let [result, setResult] = useState([
    {
      id: 1, //setOptions의 id와 구분하기 위해 100번대부터 시작
      place: 1,
      content: "2023-04-25 14:00 ~ 16:00",
      checked: false,
      people: 5,
    },
    {
      id: 2,
      place: 2,
      content: "2023-04-25 14:30 ~ 16:30",
      checked: false,
      people: 3,
    },
    {
      id: 3,
      place: 2,
      content: "2023-04-26 14:30 ~ 16:30",
      checked: false,
      people: 3,
    },
    {
      id: 4,
      place: 3,
      content: "2023-04-25 15:00 ~ 17:00",
      checked: false,
      people: 2,
    },
  ]);
  let handleOptions = (event) => {
    let newState = [...options];
    const { name } = event.target;
    newState.map((op) => {
      if (op.id === Number(name)) {
        op.checked = !op.checked;
      }
    });
    setOptions(newState);
  };
  let handleOptionsResult = (event) => {
    let newStateResult = [...result];
    const { name } = event.target;
    newStateResult.map((op) => {
      if (op.id === Number(name)) {
        op.checked = !op.checked;
      }
    });
    setResult(newStateResult);
  };
  const handleSubmit = (event) => {
    event.preventDefault();
    console.log(options);
  };

  const [meetingHour, setMeetingHour] = useState("0");
  const [meetingMin, setMeetingMin] = useState("00");

  const handleMeetingHour = (event) => {
    setMeetingHour(event.target.value);
  };
  const handleMeetingMin = (event) => {
    setMeetingMin(event.target.value);
  };

  const handleGenerateVote = () => {
    console.log("Selected time:", meetingHour, meetingMin);
    getStartDate();
    const data = {
      gid: gid,
      start_date: start_date,
      end_date: end_date,
      meetingtime: meetingHour + ":" + meetingMin,
    };
    axios
      .post(
        "https://port-0-timecodi-416cq2mlg8dr0qo.sel3.cloudtype.app/votetime",
        data,
        {
          headers: {
            Authorization: localStorage.getItem("token"),
          },
        }
      )
      .then((response) => {
        console.log(response.data);
        alert("vote success!");
      })
      .catch((err) => {
        console.log(err);
      });
  };

  return (
    <div>
      <div className="page-header">
        <h3 className="page-title">{gname}</h3>
        <nav aria-label="breadcrumb">
          <p>GID: {gid}</p>
          <p>Admin: {admin}</p>
        </nav>
      </div>
      <div className="row">
        <div className="col-6 grid-margin">
          <div className="card">
            <div className="card-body" style={{ height: "400px" }}>
              <h4 className="card-title">
                <i className="mdi mdi-bookmark-check"></i> Upcoming Meeting
              </h4>
              <p className="card-description">This is the next meeting info.</p>
              <div className="table-responsive">
                <table className="table">
                  <tr>
                    <th></th>
                    <th>Content</th>
                  </tr>
                  <tr>
                    <td className="font-weight-bold">TITLE</td>
                    <td>Band Practice</td>
                  </tr>
                  <tr>
                    <td className="font-weight-bold">WHEN</td>
                    <td>2023년 4월 25일</td>
                  </tr>
                  <tr>
                    <td className="font-weight-bold">WHERE</td>
                    <td>학생회관</td>
                  </tr>
                  <tr>
                    <td className="font-weight-bold">MEMO</td>
                    <td>Bring your headphones:)</td>
                  </tr>
                </table>
              </div>
            </div>
          </div>
        </div>
        <div className="col-6 grid-margin stretch-card">
          <div className="card">
            <h4
              className="card-title"
              style={{
                margin: "2.5vw 0 0 2.5vw",
              }}
            >
              <i className="mdi mdi-account"></i> Members
            </h4>

            <div
              className="card-body"
              style={{
                height: "200px",
                overflowY: "auto",
                overflowX: "hidden",
              }}
            >
              {/* <p className="card-description">Click member's name</p> */}
              <div className="table-responsive">
                <table className="table">
                  <thead>
                    {/* <tr style={{"text-align":'center'}}>
                      <th> Name </th>
                      <th> Actions </th>
                    </tr> */}
                  </thead>
                  <tbody>
                    {members.map(function (el, idx) {
                      return (
                        <tr>
                          <td
                            onClick={handleShow}
                            style={{ cursor: "pointer" }}
                          >
                            {el.name}
                          </td>
                          <td>
                            <button
                              type="button"
                              className="btn btn-inverse-success btn-sm"
                            >
                              TimeTable
                            </button>
                            <button
                              type="button"
                              className="btn btn-inverse-warning btn-sm"
                            >
                              Add friend
                            </button>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
            <center>
              <button
                type="button"
                className="btn btn-gradient-primary btn-sm "
                style={{ "font-weight": "420", margin: "2vw" }}
                onClick={addClose}
              >
                <i className="mdi mdi-account-plus"></i>
                &nbsp;Invite New Member
              </button>
            </center>
          </div>
        </div>
      </div>
      <div className="row">
        <GroupCalContext.Provider value={{ groupCal, fetchGroupCal }}>
          <div
            className="col grid-margin"
            style={{ height: "800px", width: "650px" }}
          >
            <div className="card" style={{ height: "750px", width: "600px" }}>
              <div className="card-body">
                <h4 className="card-title">
                  <i className="mdi mdi-calendar-multiple-check"></i> Group
                  Calender
                </h4>
                <p className="card-description">
                  Click the <span style={{ color: "#fe7c96" }}>pink box</span>{" "}
                  to see available time of the week.
                </p>
                <div style={{ "margin-top": "4vw" }}>
                  <Main gid={gid} style={{ flexDirection: "column" }} />
                  <br></br>
                  <br></br>
                </div>
              </div>
            </div>
          </div>

          <div
            className="col grid-margin"
            style={{ height: "800px", width: "540px" }}
          >
            <div className="card" style={{ height: "750px", width: "540px" }}>
              <div className="card-body">
                <div className="row">
                  <p
                    className="card-description"
                    style={{ "margin-left": "8em" }}
                  >
                    Your group members are available at..
                  </p>

                  <div
                    id="visit-sale-chart-legend"
                    className="rounded-legend legend-horizontal"
                    style={{ "margin-left": "9em" }}
                  >
                    <ul>
                      <li>
                        <span className="legend-dots bg-primary"></span>1st
                      </li>
                      <li>
                        <span
                          className="legend-dots"
                          style={{ "background-color": "#cc9fff" }}
                        ></span>
                        2nd
                      </li>
                      <li>
                        <span
                          className="legend-dots"
                          style={{ "background-color": "#e0c5ff" }}
                        ></span>
                        3rd
                      </li>
                    </ul>
                  </div>

                  <TimeTable></TimeTable>
                  <div className="row" style={{ margin: "1.5vw 0 0 3vw" }}>
                    <p
                      className="card-description"
                      style={{
                        margin: "0.2vw 1vw 0 0",
                        "text-align": "center",
                      }}
                    >
                      How long will it take?
                    </p>
                    <select
                      className="form-control form-control-sm"
                      id="meeting-hour"
                      value={meetingHour}
                      onChange={(e) => {
                        handleMeetingHour(e);
                      }}
                      style={{
                        position: "relative",
                        width: "4vw",
                        height: "2vw",
                      }}
                    >
                      <option>0</option>
                      <option>1</option>
                      <option>2</option>
                      <option>3</option>
                      <option>4</option>
                      <option>5</option>
                      <option>6</option>
                      <option>7</option>
                      <option>8</option>
                      <option>9</option>
                      <option>10</option>
                      <option>11</option>
                      <option>12</option>
                      <option>13</option>
                      <option>14</option>
                      <option>15</option>
                      <option>16</option>
                      <option>17</option>
                      <option>18</option>
                      <option>19</option>
                      <option>20</option>
                      <option>21</option>
                      <option>22</option>
                      <option>23</option>
                      <option>24</option>
                    </select>
                    <p
                      className="card-description"
                      style={{ margin: "0.2vw 0.5vw", "text-align": "center" }}
                    >
                      hours &nbsp;
                    </p>
                    <select
                      className="form-control form-control-sm"
                      id="meeting-min"
                      value={meetingMin}
                      onChange={(e) => {
                        handleMeetingMin(e);
                      }}
                      style={{
                        position: "relative",
                        width: "4vw",
                        height: "2vw",
                      }}
                    >
                      <option>00</option>
                      <option>30</option>
                    </select>
                    <p
                      className="card-description"
                      style={{ margin: "0.2vw 0.5vw", "text-align": "center" }}
                    >
                      minutes
                    </p>
                  </div>
                  <button
                    type="button"
                    className="btn btn-inverse-primary btn-sm"
                    style={{ margin: "1vw 0 0vw 12vw" }}
                    onClick={handleGenerateVote}
                  >
                    <i className="mdi mdi-calendar-plus"></i>
                    <span style={{ "font-size": "15px", "font-weight": "500" }}>
                      &nbsp; Generate Vote
                    </span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </GroupCalContext.Provider>
      </div>
      <div className="row">
        <div className="col-6 grid-margin stretch-card">
          <div className="card">
            <div
              className="card-body"
              style={{
                height: "500px",
              }}
            >
              <h4 className="card-title">
                <i className="mdi mdi-clipboard-text"></i> Vote
              </h4>
              <p className="card-description">
                Check the box to vote and submit.
              </p>

              <form onSubmit={handleSubmit}>
                <div
                  className="card-body"
                  style={{
                    height: "300px",
                    overflowY: "auto",
                    overflowX: "hidden",
                    padding: "0vw",
                  }}
                >
                  <table className="table">
                    <tr
                      style={{
                        "text-align": "center",
                      }}
                    >
                      <th>#</th>
                      <th>Time</th>
                      <th>
                        <i className="mdi mdi-checkbox-multiple-marked-outline"></i>
                      </th>
                    </tr>
                    {options.map(function (el, idx) {
                      return (
                        <tr
                          style={{
                            "text-align": "center",
                          }}
                        >
                          <td>{el.id}</td>
                          <td>{el.content}</td>
                          <td>
                            <div
                              className="form-check"
                              style={{
                                "margin-left": "3.5vw",
                              }}
                            >
                              <label className="form-check-label">
                                <input
                                  type="checkbox"
                                  className="form-check-input"
                                  checked={el.checked}
                                  onChange={handleOptions}
                                  name={el.id}
                                />
                                <i className="input-helper"></i>
                              </label>
                            </div>
                          </td>
                        </tr>
                      );
                    })}
                  </table>
                </div>

                <div className="row">
                  <button
                    type="button"
                    className="btn btn-inverse-primary btn-sm"
                    style={{ margin: "3vw 0vw 0vw 8vw" }}
                  >
                    <span style={{ "font-size": "15px", "font-weight": "500" }}>
                      &nbsp;Submit
                    </span>
                  </button>
                  <button
                    type="button"
                    className="btn btn-inverse-danger btn-sm"
                    style={{ margin: "3vw 0vw 0vw 5vw" }}
                    onClick={addClose}
                  >
                    <span style={{ "font-size": "15px", "font-weight": "500" }}>
                      &nbsp;End Vote
                    </span>
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
        <div className="col-md-6 grid-margin stretch-card">
          <div className="card">
            <div className="card-body">
              <h4 className="card-title">
                <i className="mdi mdi-poll"></i>
                Vote Result
              </h4>
              <p className="card-description">See the vote result!</p>
              <form onSubmit={handleSubmit}>
                <div
                  className="card-body"
                  style={{
                    height: "300px",
                    overflowY: "auto",
                    overflowX: "hidden",
                    padding: "0vw",
                  }}
                >
                  <table className="table">
                    <tr
                      style={{
                        "text-align": "center",
                      }}
                    >
                      <th>#</th>
                      <th>Time</th>
                      <th>
                        <i className="mdi mdi-account-multiple"></i>
                      </th>
                      <th>
                        {" "}
                        <i className="mdi mdi-checkbox-multiple-marked-outline"></i>
                      </th>
                    </tr>
                    {result.map(function (el, idx) {
                      return (
                        <tr
                          style={{
                            "text-align": "center",
                          }}
                        >
                          <td>{el.place}</td>
                          <td>{el.content}</td>
                          <td>
                            <div className="form-check">
                              <button
                                type="button"
                                className="btn btn-inverse-danger btn-sm"
                                style={{
                                  height: "1.5vw",
                                  padding: "0.1vw 0.4vw",
                                }}
                              >
                                <i className="mdi mdi-account-outline"> </i>
                                {el.people}
                              </button>
                            </div>
                          </td>
                          <td>
                            <div
                              className="form-check"
                              style={{
                                "margin-left": "2vw",
                              }}
                            >
                              <label className="form-check-label">
                                <input
                                  type="checkbox"
                                  className="form-check-input"
                                  checked={el.checked}
                                  onChange={handleOptionsResult}
                                  name={el.id}
                                />
                                <i className="input-helper"></i>
                              </label>
                            </div>
                          </td>
                        </tr>
                      );
                    })}
                  </table>
                </div>
                <button
                  type="button"
                  className="btn btn-inverse-primary btn-sm"
                  style={{ margin: "3vw 4vw 0vw 12vw" }}
                  onClick={addClose}
                >
                  <span style={{ "font-size": "15px", "font-weight": "500" }}>
                    {" "}
                    Make Meeting
                  </span>
                </button>
              </form>
            </div>
          </div>
        </div>
      </div>

      <Modal show={addShow} onHide={addClose} centered>
        <Modal.Header closeButton>
          <Modal.Title>
            {" "}
            <span style={{ "font-weight": "400", margin: "0 5vw" }}>
              Are you the Admin of this Group?
            </span>
          </Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <div className="row" style={{ margin: "0 8vw" }}>
            <button
              type="button"
              className="btn btn-primary  "
              onClick={addClose}
            >
              Yes
            </button>
            <button
              type="button"
              className="btn btn-danger  "
              onClick={friendClose}
            >
              No
            </button>
          </div>
        </Modal.Body>
      </Modal>

      <Modal show={addFriend} onHide={friendClose} centered>
        <Modal.Header closeButton>
          <Modal.Title>
            <div style={{ "font-weight": "200", margin: "0 5vw" }}>
              Sorry, you can't take this action.<br></br> Ask the Group Admin!{" "}
            </div>
          </Modal.Title>
        </Modal.Header>
        <Modal.Footer>
          <button
            type="button"
            className="btn btn-primary btn-sm"
            onClick={() => {
              friendClose();
              addClose();
            }}
          >
            OK
          </button>
          <button
            type="button"
            className="btn btn-secondary btn-sm"
            onClick={() => {
              friendClose();
            }}
          >
            Cancel
          </button>
        </Modal.Footer>
      </Modal>
      <AdminBox />
      <NonAdminBox />
    </div>
  );
}

export default Group;
