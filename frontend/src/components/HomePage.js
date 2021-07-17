import React, { Component } from 'react';
import "/static/css/createRoomPage.css"
import {Link} from 'react-router-dom'

export default function HomePage(props) {
    function checkRoom() {
        fetch("/api/checkRoom").then(res => res.json()).then((data) => {
            if (data.code) props.history.push("/room/" + data.code)
        })
    }
    checkRoom()
    return (
        <div class="mid-container">
            <h1>Listen Along</h1>
            <Link to="/join">
                <button class="create-buttons" style={{ backgroundColor: "#2aa0d1" }}>Join Room</button>
            </Link>
            <Link to="/create">
            <button class="create-buttons" style={{ backgroundColor: "#c91c49" }} >Create Room</button>
            </Link>
        </div>
    )
}
