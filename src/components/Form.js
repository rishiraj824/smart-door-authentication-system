import React, { useState } from "react";
import { Button, FormGroup, FormControl, ControlLabel } from "react-bootstrap";
import "./Form.css";
import {
  useLocation
} from "react-router-dom";
// import {useRouter} from 'react-router-dom';

export default function Login() {
  const [name, setName] = useState("");
  const [phone, setPhone] = useState("");
  const [message, setMessage] = useState("")
  const [status, setStatus] = useState(false)
  
  function useQuery() {
    return new URLSearchParams(useLocation().search);
  }
  function validateForm() {
    
    return name.length > 0 && phone.length > 0 && query.get('image')!=null
  }
  function phonehandler(e){
    if (e.length<=10){
      setPhone(e)
    }
  }
  const query = useQuery();

  function handleSubmit(event) {
    const url =
    "https://02xohgtag5.execute-api.us-west-2.amazonaws.com/prod/visitor";
    console.log("Submitted");
    console.log("Name", name, "Phone", phone);
    const data = {
      name: name,
      phoneNumber: phone,
      image: query.get('image'),  
    };
    console.log("Data is", data)
    fetch(url, {
      method: "POST",
      body: JSON.stringify(data),
      headers: {
        "Content-Type" : "application/json",
            "Access-Control-Allow-Headers" : "*",
            "Access-Control-Allow-Methods" : "OPTIONS,POST",
            "Access-Control-Allow-Credentials" : true,
            "Access-Control-Allow-Origin" : "*",
      },
    })
      .then((res) => res.json())
      .catch((error) => {
        // setMessage(JSON.parse(error))
        console.error("Error:", error)})
      .then((response) => {
        setMessage((JSON.parse(response.body).message))
        console.log("Success:", (JSON.parse(response.body)))});
      setStatus(true)
    event.preventDefault();
  }
  // console.log("Name", name)
  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        marginTop: 150,

        flexDirection: "column",
      }}
    >
      {
        query.get('image')?<img src={"https://cc-smart-door.s3-us-west-2.amazonaws.com/"+query.get('image')} alt={`${query.get('image')}`} className="photo" />
        :<div>No Image Received</div>
      }  
      {/* <img src={"https://cc-smart-door.s3-us-west-2.amazonaws.com/"+query.get('image')} alt={`${query.get('image')}`} className="photo" /> */}
      <div className="Login">
        <form onSubmit={handleSubmit}>
          <FormGroup controlId="name" bsSize="large">
            <ControlLabel>Name</ControlLabel>
            <FormControl
              autoFocus
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
          </FormGroup>
          <FormGroup controlId="phone" bsSize="large">
            <ControlLabel>Phone</ControlLabel>
            <FormControl
              value={phone}
              onChange={(e) => phonehandler(e.target.value)}
              type="number"
              
            />
          </FormGroup>
          
        </form>
      </div>
      <Button
        style={{
          marginTop: 20,
        }}
        className="btn-primary btn "
        disabled={!validateForm()}
        type="submit"
        onClick={handleSubmit}
      >
        Give access
      </Button>
      <div>
            {status && <div>{message}</div>}
      </div>
    </div>
    
  );
}
