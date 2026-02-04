from flask import Flask, render_template, request, redirect, session
import sqlite3, os

app = Flask(__name__)
app.secret_key = "skillforge_secret"

DB = "database.db"

def get_db():
    return sqlite3.connect(DB)

# ---------- INIT DB ----------
if not os.path.exists(DB):
    db = get_db()
    cur = db.cursor()
    cur.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)")
    cur.execute("CREATE TABLE progress (user TEXT, topic TEXT)")
    cur.execute("CREATE TABLE leaderboard (user TEXT, score INTEGER)")
    db.commit()
    db.close()

# ---------- AUTH ----------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]
        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT * FROM users WHERE username=? AND password=?", (u, p))
        user = cur.fetchone()
        if user:
            session["user"] = u
            return redirect("/welcome")
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]
        db = get_db()
        cur = db.cursor()
        cur.execute("INSERT INTO users VALUES (NULL, ?, ?)", (u, p))
        db.commit()
        return redirect("/")
    return render_template("register.html")

# ---------- FLOW ----------
@app.route("/welcome")
def welcome():
    return render_template("welcome.html")

@app.route("/courses")
def courses():
    return render_template("courses.html")

@app.route("/levels/<course>")
def levels(course):
    return render_template("levels.html", course=course)

@app.route("/modules/<course>/<level>")
def modules(course, level):
    modules = ["Introduction", "Core Concepts", "Advanced Topics"]
    return render_template("modules.html", course=course, level=level, modules=modules)

@app.route("/topic/<name>", methods=["GET", "POST"])
def topic(name):
    if request.method == "POST":
        db = get_db()
        cur = db.cursor()
        cur.execute("INSERT INTO progress VALUES (?, ?)", (session["user"], name))
        db.commit()
    return render_template("topic.html", name=name)

@app.route("/quiz", methods=["GET", "POST"])
def quiz():
    score = None
    if request.method == "POST":
        score = 10
        db = get_db()
        cur = db.cursor()
        cur.execute("INSERT INTO leaderboard VALUES (?, ?)", (session["user"], score))
        db.commit()
    return render_template("quiz.html", score=score)

@app.route("/leaderboard")
def leaderboard():
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT user, SUM(score) FROM leaderboard GROUP BY user")
    data = cur.fetchall()
    return render_template("leaderboard.html", data=data)

app.run(debug=True)