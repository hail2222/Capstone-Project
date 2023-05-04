import React, { useState, useRef } from 'react'
import { Modal } from "react-bootstrap";
import { Form } from 'react-bootstrap';
import FriendsTable from './FriendsTable';
import ActionButtons from './ActionButtons';

function FriendsPage() {
  const [addFriend, setFriend] = useState(false);
  const friendClose = () => setFriend(!addFriend);

  const headers = [
    {
      text : 'Name',
      value : 'name'
    },
    {
      text : 'Actions',
      value : 'actions'
    }
  ]

  const [items, setItems] = useState([
    { id : 1, name : 'Jacob',
      actions : <ActionButtons /> },
    { id : 2, name : 'John',
      actions : <ActionButtons/> },
    { id : 3, name : 'Messy',
      actions : <ActionButtons/>},
    { id : 4, name : 'Peter',
      actions : <ActionButtons/>},
    { id : 5, name : 'Dave',
      actions : <ActionButtons/>}
  ])

  const [input, setInput] = useState({
    name : ''
  })

  const {name} = input;
  const onChange = e => {
    const {name, value} = e.target;
    setInput({
      ...input,
      [name]: value
    })
  }

  const nextId = useRef(6);

  const onCreate = () => {
    const friend = {
      id: nextId.current,
      name,
      actions : <ActionButtons/>
    }
    setItems([...items, friend])
    setInput({
      name: ''
    })
    nextId.current += 1;
  }

  const onRemove = id => {
    setItems(items.filter(friend => friend.id !== id));
  }

    return (
      <div>
        <div className="page-header">
          <h3 className="page-title">
            <span className="page-title-icon bg-gradient-primary text-white mr-2">
              <i className="mdi mdi-account-star"></i>
            </span> Friends </h3>
            <button type="button" className="btn btn-inverse-primary" onClick={friendClose}>
              <span className="mr-2"><i className="mdi mdi-account-plus"></i></span>Add
            </button>
            <Modal show={addFriend} onHide={friendClose} centered>
              <Modal.Header closeButton>
                <Modal.Title>Enter your friend's ID</Modal.Title>
              </Modal.Header>
              <Modal.Body>
                <Form className="pt-3">
                  <div className="form-group">
                    <input type="text" className="form-control form-control-lg" placeholder="ID" onChange={onChange}/>
                  </div>
                </Form>
              </Modal.Body>
              <Modal.Footer>
                <button type="button" className="btn btn-primary btn-sm" onClick={onCreate}>
                  OK
                </button>
                <button type="button" className="btn btn-secondary btn-sm" onClick={friendClose}>
                  Cancel
                </button>
              </Modal.Footer>
            </Modal>
        </div>

        <div className="row">
          <div className="col-lg-12 grid-margin stretch-card">
            <div className="card">
              <div className="card-body">
                <div className="table-responsive">
                  <FriendsTable 
                    headers={headers}
                    items={items}
                  />
                </div>
              </div>
            </div>
          </div>
        </div>

      </div>
    )
  }

export default FriendsPage;