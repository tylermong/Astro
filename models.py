from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    userid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    account_creation_date = db.Column(db.DateTime, nullable=False)
    admin_status = db.Column(db.Boolean, nullable=False, default=False)
    profile_image = db.Column(db.String(255), nullable=True)
    banner_image = db.Column(db.String(255), nullable=True)


class Friend(db.Model):
    user1_id = db.Column(db.Integer, db.ForeignKey('user.userid'), nullable=False)
    user2_id = db.Column(db.Integer, db.ForeignKey('user.userid'), nullable=False)
    confirmation = db.Column(db.Integer, nullable=False, default=0)
    __table_args__ = (
        db.PrimaryKeyConstraint('user1_id', 'user2_id'),
        db.CheckConstraint('confirmation IN (0, 1)'),
    )

class Post(db.Model):
    post_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userid = db.Column(db.Integer, db.ForeignKey('user.userid'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(255), nullable=True)
    creation_date = db.Column(db.DateTime, nullable=False)
    user = db.relationship('User', backref=db.backref('posts', lazy=True))


class PrivateMessage(db.Model):
    message_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.userid'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.userid'), nullable=False)
    message_text = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(255), nullable=True)
    creation_date = db.Column(db.DateTime, nullable=False)
