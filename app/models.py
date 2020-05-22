from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask import url_for

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
    borrowed_objects = db.relationship("InventoryObject", backref='borrowed_by', lazy='dynamic')

    """URL der Profilseite"""
    def page(self):
        return url_for('user', username=self.username)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    """Setzt das Passwort für den Nutzer"""
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    """Gleicht das Passwort mit dem gespeicherten Hash ab"""
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    """Verlasse eine Organisation"""
    def leave_organisation(self, old_organisation):
        if old_organisation in self.organisations:
            self.organisations.remove(old_organisation)
            return True
        return False


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Organisation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    user = db.relationship("User", secondary='organisation_user', back_populates="organisations")
    inventoryobjects = db.relationship('InventoryObject', backref='owner', lazy=True)

    """URL der Profilseite"""
    def page(self):
        return url_for('organisation', organisation=self.name)

    """Anzahl registrierter Nutzer"""
    def user_count(self):
        return len(self.user)

    """Füge einen Nutzer hinzu"""
    def add_user(self, new_user):
        if not new_user in self.user:
            self.user.append(new_user)

    """Entferne einen Nutzer"""
    def remove_user(self, old_user):
        if old_user in self.organisations:
            self.organisations.remove(old_user)

    """Registriere einen Gegenstand"""
    def add_object(self, inv):
        if not inv in self.inventoryobjects:
            self.inventoryobjects.append(inv)

    """Lösche einen Gegenstand"""
    def delete_object(self, inv):
        if inv in self.inventoryobjects:
            self.inventoryobjects.remove(inv)

    """Verleihe einen Gegenstand"""
    def lend_object_to(self, user, object):
        assert object in self.inventoryobjects, "Object not owned by organisation"
        assert object.lend_to is None, "Object is already lent to a user"
        # success
        object.lend_to = user

    """Nimm einen Gegenstand zurück"""
    def take_back_object(self, object):
        assert object in self.inventoryobjects, "Object not owned by organisation"
        assert object.lend_to is not None, "Object is not lent to a user"
        # success
        object.lend_to = None


class InventoryObject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    article = db.Column(db.String(64), index=True)
    organisation = db.Column(db.Integer, db.ForeignKey('organisation.id'))
    description = db.Column(db.String(128), index=True)
    lend_to = db.Column(db.Integer, db.ForeignKey('user.id'))
    room = db.Column(db.Integer, db.ForeignKey('room.id'))

    """Ordne Gegenstand einem Raum/Ort zu"""
    def set_room(self, room):
        self.room = room.id


class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    inventoryobjects = db.relationship('InventoryObject', backref='in_room', lazy=True)
