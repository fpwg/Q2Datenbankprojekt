from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash

from flask_login import UserMixin


organisation_user = db.Table('organisation_user',
    db.Column('organisation_id', db.Integer, db.ForeignKey('organisation.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    organisations = db.relationship("Organisation", secondary='organisation_user', back_populates="user")

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class Organisation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    user = db.relationship("User", secondary='organisation_user', back_populates="organisations")

    def add_user(self, new_user):
        self.user.append(new_user)
