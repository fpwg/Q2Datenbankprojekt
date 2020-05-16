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
    borrowed_objects = db.relationship("InventoryObject", secondary='borrowed_by', back_populates="user")

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def add_organisation(self, new_organisation):
        self.organisations.append(new_organisation)

    def remove_organisation(self, old_organisation):
        if old_organisation in self.organisations:
            self.organisations.remove(old_organisation)
            return True
        return False

    def borrow_object(self, inv):
        if not inv in self.borrow_objects:
            self.borrow_objects.append(inv)

    def return_object(self, inv):
        if inv in self.borrowed_objects:
            self.borrowed_objects.remove(inv)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Organisation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    user = db.relationship("User", secondary='organisation_user', back_populates="organisations")
    inventoryobjects = db.relationship('InventoryObject', backref='owner', lazy=True)

    def add_user(self, new_user):
        if not new_user in self.user:
            self.user.append(new_user)

    def remove_user(self, old_user):
        if old_user in self.organisations:
            self.organisations.remove(old_user)

    def add_inventoryobject(self, inv):
        if not inv in self.inventoryobjects:
            self.inventoryobjects.append(inv)

    def remove_inventoryobject(self, inv):
        if inv in self.inventoryobjects:
            self.inventoryobjects.remove(inv)


class InventoryObject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    article = db.Column(db.String(64), index=True)
    organisation = db.Column(db.Integer, db.ForeignKey('organisation.id'), nullable=False)
    description = db.Column(db.String(128), index=True)
    lend_to = db.Column(db.Integer, db.ForeignKey('user.id'))

    def set_description(self, text):
        self.description = text

    def set_organisation(self, org):
        self.organisation = org

    def lend_to_user(self, user):
        self.lend_to = user
