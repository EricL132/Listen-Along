import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import "/static/css/createRoomPage.css"

export default function CreateRoomPage(props) {
    const [guestCanPause, setguestCanPause] = useState(props.guestCanPause ? true : false)
    const [votesToSkip, setvotesToSkip] = useState(props.votesToSkip ? props.votesToSkip : 2)
    const [message, setmessage] = useState("")


    function handleChangeControls() {
        const play = document.getElementById("play-pause")
        const noControl = document.getElementById("no-control")
        console.log(guestCanPause)
        if (guestCanPause) {

            if (noControl.classList.contains("selected")) {
                noControl.classList.remove("selected")
            }
            play.classList.add("selected")

        } else {

            if (play.classList.contains("selected")) {
                play.classList.remove("selected")
            }
            noControl.classList.add("selected")


        }

    }
    function setAllowPause() {
        if (guestCanPause === false) {
            setguestCanPause(true)
        }

    }
    function setNoControl() {
        if (guestCanPause === true) {
            setguestCanPause(false)
        }

    }
    function handleCreateRoom() {
        const votesToSkip = document.getElementById("votestoskip").value
        const guestCanPause = document.getElementById("play-pause").classList.contains("selected")
        fetch("/api/create-room", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ votesToSkip: votesToSkip, guestCanPause: guestCanPause }) }).then((res) => {
            return res.json()
        }).then((data) => {
            props.history.push('/room/' + data.code)
        })
    }
    function handleUpdateRoom(){
        const votesToSkip = document.getElementById("votestoskip").value
        const guestCanPause = document.getElementById("play-pause").classList.contains("selected")
        fetch("/api/updateroom", { method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ votesToSkip: votesToSkip, guestCanPause: guestCanPause,code:props.roomCode }) }).then((res) => {
            if(res.ok){
                setmessage("Room Updated")
                props.updateSettingsView({guestCanPause:guestCanPause,votesToSkip:votesToSkip})
            }else{
                setmessage("Failed to Update Room")
            }
        })
    }
    useEffect(() => {
        handleChangeControls()
    }, [guestCanPause])
    return (
        <>
            <div class="mid-container">
               {/*  {props.update ? <h1>Update Settings</h1> : <h1>Create Room</h1>}
                <label>Guest control settings</label>
                <div id="guest-power-container" style={{ margin: "10px" }}>

                    <div class="button-container">
                        <div class="circle-div"><button id="play-pause" onClick={setAllowPause}></button></div>
                        <label>Play/Pause</label>
                    </div>
                    <div class="button-container">
                        <div class="circle-div"><button id="no-control" onClick={setNoControl}></button></div>
                        <label>No Control</label>
                    </div>
                </div>
                <input spellCheck={false} autoComplete="off" id="votestoskip" className="creating-input" type="number" min="0" defaultValue={votesToSkip}></input>
                <label>Votes required to skip song</label>
                {!props.update? <button class="create-buttons" onClick={handleCreateRoom} style={{ backgroundColor: "#2aa0d1" }}>Create Room</button> : 
                <button class="create-buttons" onClick={handleUpdateRoom} style={{ backgroundColor: "#2aa0d1" }}>Update Room</button> 
                }
                {!props.update ?
                    <Link to="/">
                        <button class="create-buttons" style={{ backgroundColor: "#c91c49" }}>Back</button>
                    </Link>
                    : null}
                <span style={{position:"absolute",top:"60%"}}>{message}</span> */}
            </div>

        </>
    )

}