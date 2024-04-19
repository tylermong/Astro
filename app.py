from flask import Flask, render_template, request, redirect, url_for, session, abort
from flask_sqlalchemy import SQLAlchemy
from models import db, User, Friend, Post, PrivateMessage
from datetime import datetime
import argon2
import math
import re

hasher = argon2.PasswordHasher()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.secret_key = '7c19a9c83258791f711591a505b467d9'

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return 'Hello, World!'

@app.route("/")
def home():
    return "send to main page if not logged in"


@app.route('/login', methods=['GET', 'POST'])
def login():
    # on post request recieved
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()

        if user and argon2.PasswordHasher().verify(user.password, password):
            # set session variable
            session['user_id'] = user.userid
            return redirect(url_for('profile', username=user.username))  # Redirect to user's profile
        else:
            # return error message
            msg = 'Invalid username or password'
            return render_template('login.html', msg=msg)

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    login_status = require_login_status(must_be_logged_out=True)
    if login_status is not None:
        return login_status

    # default output message
    msg = ''
    # Check if "username", "password" and "email" exist
    if (request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in
            request.form):

        # Create variables for easy access
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        confirmPassword = request.form['confirm-password']

        # Check if account exists using SQLAlchemy
        account = User.query.filter_by(username=username).first()

        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif len(password) < 5:
            msg = 'Password too short!'
        elif password != confirmPassword:
            msg = 'Passwords do not match!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            # Proceed with account creation
            hashed_password = hasher.hash(password)
            new_user = User(username=username, password=hashed_password, email=email, account_creation_date=datetime.now(), profile_image=".images\required\Default_Profile_Picture.png")
            db.session.add(new_user)
            db.session.commit()
            msg = 'You have successfully registered!'
            return render_template('register.html', msg=msg)
        
    elif request.method == 'POST':
        # Form is empty
        msg = 'Please fill out the form!'

    # Show registration form with message (if any)
    return render_template('register.html', session=session, msg=msg)

# example on how to link to profile {{ url_for('profile', username=user.username) }}
@app.route('/profile/<username>')
def profile(username):
    user = User.query.filter_by(username=username).first()
    if user:
        return render_template('profile.html', user=user)
    else:
        # Handle the case where the user is not found
        return render_template('profile_not_found.html', username=username)


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
