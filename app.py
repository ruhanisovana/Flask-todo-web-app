from flask import Flask, render_template, request, redirect, flash, session
import os
from cs50 import SQL
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.secret_key = "your_secret_key"

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

if not os.path.exists("todo.db"):
    open("todo.db", "w").close()

db = SQL("sqlite:///todo.db")

db.execute("""CREATE TABLE IF NOT EXISTS user (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT)""")
db.execute("""CREATE TABLE IF NOT exists tasks (id INTEGER PRIMARY KEY AUTOINCREMENT, task TEXT NOT NULL, done INTEGER DEFAULT 0, user_id INTEGER, priority TEXT, FOREIGN KEY(user_id) REFERENCES users(id))""")
@app.route("/", methods=["POST", "GET"])
def index():

    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]

    if request.method == "POST":

        print("Form data:", request.form)

        task = request.form.get("task")
        priority = request.form.get("priority")
        print(task, priority)

        if not task:
            print("No task:", task)
            flash("Task should be filled ⚠️")
            return redirect("/")

        db.execute("INSERT INTO tasks (task, done, priority, user_id) VALUES (?, ?, ?, ?)", task, 0, priority, user_id)
        print("Insert task:", task)
        flash("Task added successfully 💯")
        return redirect("/")

    filter_type = request.args.get("filter", "all")

    if filter_type == "done":
        tasks = db.execute("SELECT * FROM tasks WHERE user_id = ? AND done = 1", user_id)
    elif filter_type == "pending":
        tasks = db.execute("SELECT * FROM tasks WHERE user_id = ? AND done = 0", user_id)
    else:
        tasks = db.execute("SELECT * FROM tasks WHERE user_id = ?", user_id)

    return render_template("index.html", tasks=tasks, filter_type=filter_type)


@app.route("/signup", methods=["GET", "POST"])
def signup():

    print("signup Route hit")

    if request.method == "GET":
        print("GET request received")
        return render_template("signup.html")

    username = request.form.get("username")
    password = request.form.get("password")

    print("username:", username)
    print("password:", password)

    if not username or not password:
        flash("fill all requirements")
        return redirect("/signup")

    hash_pw = generate_password_hash(password)

    try:
        db.execute("INSERT INTO users (username, password) VALUES (?, ?)", username, hash_pw)

    except Exception as e:
         print("ERROR:", e)
         flash("username already exists")
         return redirect("/signup")

    flash("signup successful")
    return redirect("/login")


@app.route("/login", methods=["GET", "POST"])
def login():

    session.clear()

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:

            flash("user not found👎")
            return redirect("/login")

        user = db.execute("SELECT * FROM users WHERE username = ?", username)

        if not check_password_hash(user[0]["password"], password):
            flash("invalid password ⚠️")
            return redirect("/login")

        session["user_id"] = user[0]["id"]

        flash("Logged in 👍✅")
        return redirect("/")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("logged out⬅️")
    return redirect("/login")

@app.route("/toggle/<int:id>", methods=["POST"])
def toggle(id):

    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]

    print(" TOGGLE ROUTE HIT")

    print("1. Toggle called with id:", id)

    task = db.execute("SELECT * FROM tasks WHERE id = ? AND user_id = ?", id, user_id)
    print("2. TASK:", task)
    print("ALL TASK:", db.execute("SELECT * FROM tasks"))

    if task:
        current = task[0]["done"]
        print("3. current value:", current)

        new_value = 0 if current else 1
        print("4. new value:", new_value)

        db.execute("UPDATE tasks SET done = ? WHERE id = ? AND user_id = ?", new_value, id, user_id)
        flash("Task marked ✅")
        print("5. update DB")
    return redirect("/")

@app.route("/edit/<int:id>", methods=["POST", "GET"])
def edit(id):

    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]

    if request.method == "POST":
        task = request.form.get("task")
        priority = request.form.get("priority")

        if not task:
            return"Missing task"

        db.execute("UPDATE tasks SET task = ?, priority = ? WHERE id = ? AND user_id = ?", task, priority, id, user_id)
        flash("Task Updated successfully 👏")
        return redirect("/")

    else:
        task = db.execute("SELECT * FROM tasks WHERE id = ? AND user_id = ?", id, user_id)

        if len(task) == 0:
            flash("Task not found")
            return redirect("/")

        return render_template("edit.html", task=task[0])

@app.route("/delete/<int:id>", methods=["POST"])
def delete(id):

    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]

    db.execute("DELETE FROM tasks WHERE id = ? AND user_id = ?", id, user_id)
    flash("Task Deleted 👍")
    return redirect("/")




























