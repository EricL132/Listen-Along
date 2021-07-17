import React, { Component } from "react";
import { render } from "react-dom";
import HomePage from './HomePage'
import RoomJoinPage from './RoomJoinPage';
import CreateRoomPage from './CreateRoomPage';
import Room from './Room';
import { BrowserRouter as Router, Switch, Route, Link, Redirect } from "react-router-dom";

export default function App() {

    return (
        <div class="mid-page">
            <Router>
                <Switch>
                    <Route path="/" exact>{HomePage}</Route>
                    <Route path="/join" component={RoomJoinPage}></Route>
                    <Route path="/create" component={CreateRoomPage}></Route>
                    <Route path="/room/:roomCode" component={Room}></Route>
                </Switch>
            </Router>
        </div>

    )

}



render(<App />, document.getElementById("app"))