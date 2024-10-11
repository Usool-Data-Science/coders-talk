from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import random
from typing import Dict, Any, Optional

app: Flask = Flask(__name__)
socketio: SocketIO = SocketIO(app)

# Dictionary to store connected users and their details
users: Dict[str, Dict[str, str]] = {}

@app.route('/')
def index() -> str:
    """
    Route to render the index page.

    Returns:
        str: HTML content for the index page.
    """
    return render_template('index.html')


@socketio.on("connect")
def handle_connect() -> None:
    """
    Event handler for user connection.

    Assigns a random username and avatar to the connected user and 
    emits this information to all connected users.
    """
    username: str = f"User_{random.randint(1000, 9999)}"
    gender: str = random.choice(["girl", "boy"])
    avatar_url: str = f"https://avatar.iran.liara.run/public/{gender}?username={username}"

    # Store user information using the session ID as key
    users[request.sid] = {"username": username, "avatar": avatar_url}

    # Broadcast that a new user has joined
    emit("user_joined", {"username": username, "avatar": avatar_url}, broadcast=True)

    # Send the assigned username to the connected user
    emit("set_username", {"username": username})


@socketio.on("disconnect")
def handle_disconnect() -> None:
    """
    Event handler for user disconnection.

    Removes the user from the active users list and broadcasts the user's 
    departure to all connected users.
    """
    user: Optional[Dict[str, str]] = users.pop(request.sid, None)
    if user:
        emit("user_left", {"username": user["username"]}, broadcast=True)


@socketio.on("send_message")
def handle_message(data: Dict[str, Any]) -> None:
    """
    Event handler for receiving a message from a user.

    Broadcasts the message along with the username and avatar of the sender
    to all connected users.

    Args:
        data (Dict[str, Any]): Data containing the message sent by the user.
    """
    user: Optional[Dict[str, str]] = users.get(request.sid)
    if user:
        emit("new_message", {
            "username": user["username"],
            "avatar": user["avatar"],
            "message": data["message"]
        }, broadcast=True)


@socketio.on("update_username")
def handle_update_username(data: Dict[str, Any]) -> None:
    """
    Event handler for updating a user's username.

    Updates the username of the user and broadcasts the change to all connected users.

    Args:
        data (Dict[str, Any]): Data containing the new username.
    """
    old_username: str = users[request.sid]["username"]
    new_username: str = data["username"]
    users[request.sid]["username"] = new_username

    emit("username_updated", {
        "old_username": old_username,
        "new_username": new_username
    }, broadcast=True)


if __name__ == "__main__":
    socketio.run(app)
