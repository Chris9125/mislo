import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for, flash
from flask_session import Session
from flask_socketio import SocketIO, emit
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

# Configure application
app = Flask(__name__)
io = SocketIO(app, engineio_logger=True, logger=True, cors_allowed_origins="*")

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///study.db")

if __name__ == '__main__':
    io.run(app, debug=True)

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@io.on("connect")
def set_sid():
    db.execute("UPDATE users SET user_sid = ? WHERE user_id = ? ", request.sid, session['user_id'])
    user = session['name']
    emit('userConnected', user, json=True, broadcast=True)

@app.route("/", methods = ["GET","POST"])
@login_required
def index():
    session["users"] = db.execute("SELECT user_id, username, user_sid FROM users")
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("Must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("Must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["password_hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["user_id"]
        session["name"] = rows[0]["username"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method=="POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        email = request.form.get("email")

        if (password == " "):
            return apology("Invalid Characters", 400)

        if (password != confirmation):
            return apology("The passwords are different", 400)


        password = generate_password_hash(password)

        if (not password or not username or not confirmation or not email):
            return apology("Invalid username or password", 400)

        try:
            db.execute("INSERT INTO users (username, password_hash, email) VALUES (?, ?, ?)", username, password, email)
        except:
            return apology("Username already exists", 400)

        return render_template("login.html")

    return render_template("register.html")

@app.route("/myrooms", methods = ["POST","GET"])
@login_required
def myrooms():
    return render_template("myrooms.html")

@app.route("/rooms", methods = ["POST","GET"])
@login_required
def rooms():
    rooms = db.execute("SELECT * FROM study_rooms")
    return render_template("rooms.html", rooms=rooms)

@app.route("/create_room", methods = ["POST","GET"])
@login_required
def create_room():
    if request.method == "POST":
        try:
            name = request.form.get("name")
            description = request.form.get("description")
            db.execute("INSERT into study_rooms (room_name, description, creator_id) VALUES (?, ?, ?)",
                    name, description, session['user_id'])
            flash("Room Created Successfully")
        except:
            flash("Room Creation Failed")
            return redirect("/rooms")

        return redirect("/rooms")
    return render_template("create_room.html")

@app.route("/enter_room", methods=["POST","GET"])
@login_required
def entering():
    room = request.args.get("room")

    if (not room):
        room = session['last_room']

    session["last_room"] = room
    users = db.execute("SELECT * FROM users ORDER BY user_id")
    content = db.execute("SELECT * FROM shared_resources WHERE room_id  = ?", room)
    return render_template("room.html", room=room, content=content, users=users, int=int)

@app.route("/new_post", methods=["POST", "GET"])
@login_required
def posting():

    if request.method == "POST":
        try:
            post_type=request.form.get("post_op")
            content=request.form.get("content")
            db.execute("INSERT INTO shared_resources ('room_id', 'user_id', 'resource_type', 'resource_content') VALUES (?, ?, ?, ?)", session['last_room'], session['user_id'], post_type, content)
            flash("Post Created Successfully")
            return redirect(url_for("entering", room=session['last_room']))
        except:
            return apology("Error when creating post", 400)

    return render_template("newpost.html")

@app.route("/my_rooms", methods=["POST", "GET"])
@login_required
def rooms2():
    rooms = db.execute("SELECT * FROM study_rooms WHERE creator_id = ?", session['user_id'])
    return render_template("my_rooms.html", rooms=rooms)

@io.on('sendMessage')
@login_required
def message_handler(msg):
    users = db.execute("SELECT * FROM users")
    for user in users:
        if (msg['nome'] == user['username']):
            db.execute("INSERT INTO chat_messages (user_id, message_content, user_id_sent) VALUES (?, ?, ?)", session['user_id'], msg["message"], user['user_id'])
            msg['nome'] = session['name']
            mysid = request.sid
            emit('getm', msg, json=True, to=(user['user_sid'], mysid))

@app.route('/get_users')
@login_required
def user_query():
    users = db.execute("SELECT * FROM users");
    return users

@io.on('getConversation')
@login_required
def getMessages(name):
    for user in session['users']:
        if (user['username'] == name):
            messages = db.execute("SELECT message_content, t1.user_id, t2.username FROM chat_messages as t1 JOIN users as t2 ON t1.user_id = t2.user_id WHERE (t1.user_id = ? AND t1.user_id_sent = ?) OR (t1.user_id_sent = ? AND t1.user_id = ?)", session['user_id'], user['user_id'], session['user_id'], user['user_id'])
            emit('getConversation', messages, json=True, to=request.sid)


