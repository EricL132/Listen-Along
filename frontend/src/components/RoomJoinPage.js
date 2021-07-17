import React, { Component, useState } from 'react';
import { Link } from 'react-router-dom'
import "/static/css/createRoomPage.css"


export default function RoomJoinPage(props) {
    const [errorMessage,seterrorMessage] = useState()
    function handleJoinRoom(){
        const code = document.getElementById("invitecode").value
        fetch("/api/join-room",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({code:code})}).then((res)=>{
            if(res.ok){
                props.history.push("/room/"+code)
            }else{
                seterrorMessage("Invalid Room Code")
            }
        })
    }
    return (
        <div class="mid-container">
            <h1>Join Room</h1>
            <input spellCheck={false} autoComplete="off" id="invitecode" class="creating-input" placeholder="Room Code"></input>
            <button class="create-buttons" style={{ backgroundColor: "#2aa0d1"}} onClick={handleJoinRoom}>Join Room</button>
            <Link to="/">
                <button class="create-buttons" style={{ backgroundColor: "#c91c49" }}  >Back</button>
            </Link>
            <span style={{position:"absolute",marginTop:"15rem",fontWeight:"bold"}}>{errorMessage}</span>
        </div>
    )

}