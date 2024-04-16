from flask import Flask, render_template, request, redirect, url_for, session, abort

app = Flask(__name__)

@app.route("/")
def home():
    return "send to main page if not logged in"

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/profile")
def profile():
    return render_template("profile.html")

@app.route("/messages")
def messages():
    return render_template("messages.html")

@app.route("/settings")
def settings():
    return render_template("settings.html")

@app.route("/notifications")
def notifications():
    return render_template("notificiations.html")

if __name__ == '__main__':
    app.run()
