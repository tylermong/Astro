import os
from flask import Flask, flash, render_template, request, redirect, send_from_directory, url_for, session, abort
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from models import db, User, Friend, Post, PrivateMessage
from datetime import datetime
import argon2
from argon2.exceptions import VerifyMismatchError
import math
import re

hasher = argon2.PasswordHasher()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.secret_key = '7c19a9c83258791f711591a505b467d9'
app.config['UPLOAD_FOLDER'] = 'static/images/userposted'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # limit uploads to 16MB
FILETYPES = {'png', 'jpg', 'jpeg', 'gif'}

db.init_app(app)

with app.app_context():
    db.create_all()


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in FILETYPES


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.before_request
def require_login():
    open_routes = ['login', 'register', 'static']
    if not session.get('loggedin') and request.endpoint not in open_routes:
        return redirect(url_for('login'))


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        content = request.form['content']
        image = request.files['image']
        image_url = None

        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image_name = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_name)
            os.makedirs(os.path.dirname(image_path), exist_ok=True)
            image.save(image_path)
            image_url = url_for('uploaded_file', filename=image_name)

        new_post = Post(userid=session["id"], content=content, image_url=image_url, creation_date=datetime.now())
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for('home'))

    page = int(request.args.get('page', default='1'))
    count = int(request.args.get('count', default='10'))
    show_friends = request.args.get('show_friends', 'no')

    user_id = session.get('id', None)
    if user_id:
        if show_friends == 'yes':
            friend_ids = db.session.query(Friend.user2_id).filter(Friend.user1_id == user_id, Friend.confirmation == 1).all()
            friend_ids += db.session.query(Friend.user1_id).filter(Friend.user2_id == user_id, Friend.confirmation == 1).all()
            friend_ids = {fid[0] for fid in friend_ids} # stop duplicates froms showing

            posts_query = Post.query.filter(Post.userid.in_(friend_ids)).order_by(Post.creation_date.desc())
        else:
            posts_query = Post.query.order_by(Post.creation_date.desc())

        total_posts = posts_query.count()
        total_pages = math.ceil(total_posts / count)
        offset = (page - 1) * count
        posts = posts_query.offset(offset).limit(count).all()

        return render_template('home.html', posts=posts, total_pages=total_pages, page=page, count=count, show_friends=show_friends)
    else:
        return redirect(url_for('login'))


from argon2.exceptions import VerifyMismatchError

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username').strip().lower()
        password = request.form.get('password').strip()
        
        user = User.query.filter(User.username.ilike(username)).first()

        if user:
            try:
                if argon2.PasswordHasher().verify(user.password, password):
                    session['loggedin'] = True
                    session['id'] = user.userid
                    session['username'] = user.username
                    session['profile_image'] = user.profile_image
                    session['admin'] = bool(user.admin_status)

                    return redirect(url_for('profile', username=user.username))
                else:
                    msg = 'Invalid username or password'
            except VerifyMismatchError:
                msg = 'Invalid username or password'
        else:
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

    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'confirm-password' in request.form and 'email' in request.form:
        email = request.form['email'].strip()
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        confirmPassword = request.form['confirm-password'].strip()

        account = User.query.filter(User.username.ilike(username)).first()

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
            hashed_password = hasher.hash(password)
            new_user = User(username=username, password=hashed_password, email=email, account_creation_date=datetime.now(), profile_image="/static/images/required/Default_Profile_Picture.png", banner_image="/static/images/required/Default_Banner_Picture.png")
            db.session.add(new_user)
            db.session.commit()
            msg = 'You have successfully registered!'
            return render_template('register.html', session=session, msg=msg)

    elif request.method == 'POST':
        msg = 'Please fill out the form!'

    return render_template('register.html', session=session, msg=msg)



from sqlalchemy import or_, and_

@app.route('/profile/<username>')
def profile(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        return "No profile found!", 404

    show_friend_request_button = False

    if 'id' in session and user.userid != session['id']:
        show_friend_request_button = True

        friend_request = Friend.query.filter(
            or_(
                and_(Friend.user1_id == session['id'], Friend.user2_id == user.userid),
                and_(Friend.user1_id == user.userid, Friend.user2_id == session['id'])
            )
        ).first()

        if friend_request:
            if friend_request.confirmation == 1:
                show_friend_request_button = False
            elif friend_request.confirmation == 0:
                if friend_request.user2_id == session['id']:
                    show_friend_request_button = True
                else:
                    show_friend_request_button = False

    count = 15
    page = int(request.args.get('page', 1))
    posts = Post.query.filter_by(userid=user.userid).order_by(Post.creation_date.desc()).paginate(page=page, per_page=count)

    return render_template('profile.html', session=session, username=username, user=user, posts=posts,
                           show_friend_request_button=show_friend_request_button)






@app.route('/delete_post/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    post = Post.query.get(post_id)
    if not post:
        return "Post not found!", 404

    if post.userid != session.get('id'):
        return "You are not authorized to delete this post.", 403

    db.session.delete(post)
    db.session.commit()

    user = User.query.get(post.userid)
    if user:
        return redirect(url_for('profile', username=user.username))
    return redirect(url_for('index'))



@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if 'loggedin' not in session:
        return redirect(url_for('login'))

    user_id = session['id']
    user = User.query.get(user_id)

    if request.method == 'POST':
        username = request.form['username'].strip()
        email = request.form['email'].strip()
        profile_image = request.files['profile_image']
        banner_image = request.files['banner_image']

        if username != user.username:
            if User.query.filter_by(username=username).first():
                flash('This username is already taken. Please choose a different one.')
                return render_template('edit_profile.html', user=user)

        if profile_image and allowed_file(profile_image.filename):
            filename = secure_filename(profile_image.filename)
            profile_image_name = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
            profile_image_path = os.path.join(app.config['UPLOAD_FOLDER'], profile_image_name)
            os.makedirs(os.path.dirname(profile_image_path), exist_ok=True)
            profile_image.save(profile_image_path)
            user.profile_image = url_for('uploaded_file', filename=profile_image_name)

        if banner_image and allowed_file(banner_image.filename):
            filename = secure_filename(banner_image.filename)
            banner_image_name = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
            banner_image_path = os.path.join(app.config['UPLOAD_FOLDER'], banner_image_name)
            os.makedirs(os.path.dirname(banner_image_path), exist_ok=True)
            banner_image.save(banner_image_path)
            user.banner_image = url_for('uploaded_file', filename=banner_image_name)

        user.username = username
        user.email = email
        db.session.commit()

        session['username'] = username

        return redirect(url_for('profile', username=username))

    return render_template('edit_profile.html', user=user)



@app.route("/messages")
def messages():
    return render_template("messages.html", session=session)


@app.route("/settings")
def settings():
    return render_template("settings.html", session=session)


@app.route('/notifications')
def notifications():
    if 'id' not in session:
        return redirect(url_for('login'))

    user_id = session['id']
    friend_requests = Friend.query.filter_by(user2_id=user_id, confirmation=0).all()
    current_user = User.query.get(user_id) 

    senders = {}
    for request in friend_requests:
        sender_id = request.user1_id if request.user1_id != user_id else request.user2_id
        senders[sender_id] = User.query.get(sender_id)

    return render_template("notifications.html", friend_requests=friend_requests, current_user=current_user, senders=senders)


@app.route('/create_post', methods=['POST'])
def create_post():
    if 'username' in session:
        username = session['username']
        user = User.query.filter_by(username=username).first()
        if user:
            content = request.form.get('content')
            image_url = request.form.get('image_url')

            new_post = Post(userid=user.userid,
                            content=content,
                            image_url=image_url,
                            creation_date=datetime.now())

            db.session.add(new_post)
            db.session.commit()

            return redirect(url_for('home'))
        else:
            return "User not found", 404
    else:
        return redirect(url_for('login'))

@app.route('/send_friend_request/<username>')
def send_friend_request(username):
    sender_id = session.get('id')
    receiver = User.query.filter_by(username=username).first()

    existing_request = Friend.query.filter_by(user1_id=sender_id, user2_id=receiver.userid, confirmation=0).first()

    if receiver and sender_id != receiver.userid:
        if existing_request:
            existing_request.confirmation = 1
        else:
            new_friend_request = Friend(user1_id=sender_id, user2_id=receiver.userid, confirmation=0)
            db.session.add(new_friend_request)
        db.session.commit()
        return redirect(url_for('profile', username=receiver.username))
    else:
        return "Invalid request"


@app.route('/accept_friend_request/<int:user1_id>')
def accept_friend_request(user1_id):
    if 'id' not in session:
        return redirect(url_for('login'))

    friend_request = Friend.query.filter_by(user1_id=user1_id, user2_id=session['id']).first()
    if friend_request:
        friend_request.confirmation = 1
        db.session.commit()
        return redirect(url_for('notifications'))
    else:
        return "Invalid request"

@app.route('/delete_friend_request/<int:user1_id>')
def delete_friend_request(user1_id):
    if 'id' not in session:
        return redirect(url_for('login'))

    friend_request = Friend.query.filter_by(user1_id=user1_id, user2_id=session['id']).first()
    if friend_request:
        db.session.delete(friend_request)
        db.session.commit()
        return redirect(url_for('notifications'))
    else:
        return "Invalid request"


def require_login_status(must_be_logged_out=False, must_be_admin=False, destination='profile'):
    if 'loggedin' not in session.keys() and not must_be_logged_out:
        return redirect(url_for('login') + '?destination=' + destination)

    if 'loggedin' in session.keys() and must_be_logged_out:
        return redirect('/' + destination)

    if must_be_admin and not session['admin']:
        abort(403)

if __name__ == '__main__':
    app.run(port=45710)
