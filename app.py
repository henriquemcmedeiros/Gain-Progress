import os
import datetime

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from functions import login_required

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///registrants.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """All the structures for an autorized enviroment"""
    user_id = session["user_id"]
    if user_id == 5:
        return redirect("/admin")
    username_db = db.execute("SELECT username FROM users WHERE id = ?", user_id)
    username = username_db[0]["username"]
    lastTimeUpdated = db.execute("SELECT lastTimeUpdated FROM 'materias'")

    return render_template("index.html", username=username, lastTimeUpdated=lastTimeUpdated)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        username = request.form.get("username")
        # Ensure username was submitted
        if not request.form.get("username"):
            return flash("Must give Username")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return flash("Must give Password")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return flash("Wrong Password")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "GET":
        return render_template("register.html")
    else:
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmPassword")

        if not username:
            return flash("Must give Username")
        if not password:
            return flash("Must give Password")
        if not confirmation:
            return flash("Must give Confirmation")
        if password != confirmation:
            return flash("Passwords don't match")



        hash = generate_password_hash(password)

        try:
            new_user = db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, hash)
        except:
            return flash("Username already exist")

        session["user_id"] = new_user

        return redirect("/")

@app.route("/admin", methods=["GET", "POST"])
@login_required
def admin():
        users = db.execute("SELECT id, username FROM 'users' ORDER BY id")
        materias = ["PI2", "BD", "GA", "AP2", "C1", "ECS", "OAC"]

        lastTimeUpdated = db.execute("SELECT lastTimeUpdated FROM 'materias'")

        return render_template("admin.html", users=users, materias=materias, lastTimeUpdated=lastTimeUpdated)

@app.route("/deregister", methods=["POST"])
def deregister():
    id = request.form.get("id")
    if id:
        db.execute("DELETE FROM 'users' WHERE id = ?", id)
    return redirect("/admin")

@app.route("/lastTimeUpdated", methods=["POST"])
def lastTimeUpdated():
    materia = request.form.get("materias")
    if materia:
        lastTimeUpdate = datetime.datetime.now()
        db.execute("UPDATE 'materias' SET lastTimeUpdated = ? WHERE materia = ?", lastTimeUpdate, materia)
    return redirect("/admin")