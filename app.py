import os
from flask import Flask, render_template, request, redirect, url_for, session, abort
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

db = SQLAlchemy(app)

class User(db.Model):
    userid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    account_creation_date = db.Column(db.DateTime, nullable=False)
    admin_status = db.Column(db.Boolean, nullable=False, default=False)

class Friend(db.Model):
    user1_id = db.Column(db.Integer, db.ForeignKey('user.userid'), nullable=False)
    user2_id = db.Column(db.Integer, db.ForeignKey('user.userid'), nullable=False)
    confirmation = db.Column(db.Integer, nullable=False, default=0)
    __table_args__ = (
        db.PrimaryKeyConstraint('user1_id', 'user2_id'),
        db.CheckConstraint('confirmation IN (0, 1)'),
    )

class Post(db.Model):
    userid = db.Column(db.Integer, db.ForeignKey('user.userid'), nullable=False)
    user_post_id = db.Column(db.Integer, nullable=False)
    content = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(255))
    creation_date = db.Column(db.DateTime, nullable=False)
    __table_args__ = (
        db.PrimaryKeyConstraint('userid', 'user_post_id'),
    )

class PrivateMessage(db.Model):
    message_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.userid'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.userid'), nullable=False)
    message_text = db.Column(db.Text)
    image_url = db.Column(db.String(255))
    creation_date = db.Column(db.DateTime, nullable=False)

with app.app_context():
    db.create_all()


@app.route('/')
def index():
    return 'Hello, World!'

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
    return render_template("notifications.html")


# check status of user
def require_login_status(must_be_logged_out=False, must_be_admin=False, destination='profile'):
    if 'loggedin' not in session.keys() and not must_be_logged_out:
        return redirect(url_for('login') + '?destination=' + destination)

    if 'loggedin' in session.keys() and must_be_logged_out:
        return redirect('/' + destination)

    if must_be_admin and not session['admin']:
        abort(403)

if __name__ == '__main__':
    app.run()
