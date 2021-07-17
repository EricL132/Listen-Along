import React, { useState, useEffect } from "react"
import CreateRoomPage from './CreateRoomPage'

let interval;
let title;
export default function Room(props) {
    const [votesToSkip, setvotesToSkip] = useState(2)
    const [guestCanPause, setguestCanPause] = useState(false)
    const [code, setCode] = useState()
    const [isHost, setisHost] = useState()
    const [showSettings, setshowSettings] = useState(false)
    const [spotifyAuthenticated, setspotifyAuthenticated] = useState(false)
    const [song, setsong] = useState()
    const [barlength, setbarlength] = useState()
  
    function getRoom() {
        fetch("/api/get-room?code=" + props.match.params.roomCode).then((res) => {
            if (!res.ok) {
                handleLeaveRoom()
            }

            return res.json()
        }
        ).then((data) => {
            console.log(data)
            setvotesToSkip(data.votesToSkip)
            setguestCanPause(data.guestCanPause)
            setisHost(data.isHost)
            setCode(data.code)
            authSpotify()
            
        })
    }
    function getCurrentSong() {
        fetch('/spotify/currentsong').then((res) => {
            if (!res.ok) {
                return {}
            } else {
                return res.json()
            }
        }).then((data) => {
            console.log(title)
              if(data.title!==title && !data.ishost){
                fetch('/spotify/usersong',{ method: "POST", headers: { "Content-Type": "application/json" },body:JSON.stringify({songuri:data.uri}) }).then((res)=>res.json()).then((data)=>{
                    
                })
            } 
            setsong(data)
            title=data.title
            setbarlength((data.progress / data.duration) * 100);
            
        })
    }
    function authSpotify() {
        fetch('/spotify/checkauth').then((res) => res.json()).then((data) => {
            setspotifyAuthenticated(data.status)
            if (!data.status) {
                fetch('/spotify/getauth').then((res) => res.json()).then((data) => {
                    window.location.replace(data.url)
                })
            }
        })
    }

    function handleLeaveRoom() {
        fetch('/api/leaveroom', { method: "POST", headers: { "Content-Type": "application/json" } }).then((_res) => {
            props.history.push("/")
        })
    }

    function handlePlaySetting() {
        if (song.current) {
            fetch("/spotify/pause", { method: "PUT", headers: { "Content-Type": "application/json" } })
            setsong((prev) => ({ ...prev, current: false }))
        } else {
            fetch("/spotify/play", { method: "PUT", headers: { "Content-Type": "application/json" } })
            setsong((prev) => ({ ...prev, current: true }))
        }
    }
    function handleSkip() {
        fetch("/spotify/skip", { method: "POST", headers: { "Content-Type": "application/json" } })
    }
    function handlePrevSong(){
        fetch("/spotify/previous", { method: "POST", headers: { "Content-Type": "application/json" } })
    }
    function copyCode(){
        var dummy = document.createElement("input")
        document.body.append(dummy)
        dummy.value = code
        dummy.select()
        document.execCommand("copy")
        document.body.removeChild(dummy)
    }
    useEffect(() => {
        getRoom()
        // getCurrentSong()
        interval = setInterval(() => { getCurrentSong() }, 1000)
    }, [])




    useEffect(() => {
        return () => {
            clearInterval(interval)
        }
    }, [])
    return (
        <>
            {!showSettings ?
                <div class="mid-container">

                    {song ?
                        <>
                            <div id="song-info-container">
                                <img src={song.image}></img>

                                <span class="song-info-span">{song.title}</span>
                                <span class="song-info-span" style={{ fontSize: "12px", opacity: ".7" }}>{song.artist}</span>
                            </div>
                            <div id="play-setting-container">
                                {song.prev_votes > 0 ? <span>{song.prev_votes}/{song.required_to_skip}</span> : null}

                                <button onClick={handlePrevSong}><i class="fas fa-step-backward"></i></button>
                                {song.current ? <button onClick={handlePlaySetting}><i class="fas fa-pause"></i></button> : <button onClick={handlePlaySetting}><i class="fas fa-play"></i></button>}

                                <button id="skip-button" onClick={handleSkip}><i class="fas fa-step-forward"></i></button>
                                {song.votes > 0 ? <span>{song.votes}/{song.required_to_skip}</span> : null}
                            </div>
                            <div id="play-bar"><div id="play-time" style={{ width: `${barlength}%` }}></div></div>
                            <div id="spot-song" >
                            </div>

                        </>
                        : null}
                    <div>
                        <span class="song-info-span" id="room-code" style={{ marginTop: "1rem" }}>Room: {code}</span>
                        <button id="copy-button" onClick={copyCode}><i class="fas fa-copy"></i></button>
                    </div>

                    {isHost ?
                        <button class="create-buttons" style={{ backgroundColor: "#2aa0d1" }} onClick={() => setshowSettings(true)}>Settings</button>

                        : null}
                    <button class="create-buttons" style={{ backgroundColor: "#c91c49" }} onClick={handleLeaveRoom}>Leave Room</button>
                </div>
                :
                <>
                    <CreateRoomPage
                        update={true}
                        votesToSkip={votesToSkip}
                        guestCanPause={guestCanPause}
                        roomCode={code}
                        updateSettingsView={(data) => {
                            setvotesToSkip(data.votesToSkip)
                            setguestCanPause(data.guestCanPause)
                        }}
                    />
                    <button class="create-buttons" style={{ backgroundColor: "#c91c49", position: "absolute", top: "55%" }} onClick={() => setshowSettings(false)}>Close</button>
                </>
            }
        </>
    )
}