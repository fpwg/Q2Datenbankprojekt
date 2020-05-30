from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask import url_for

from flask_login import UserMixin


category_inventoryobject = db.Table('category_organisation',
    db.Column('category_id', db.Integer, db.ForeignKey('category.id'), primary_key=True),
    db.Column('inventoryobject_id', db.Integer, db.ForeignKey('inventory_object.id'), primary_key=True)
)


class Lend_Objects(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    inventory_object_id = db.Column(db.Integer, db.ForeignKey("inventory_object.id"), primary_key=True)

    user = db.relationship('User', back_populates="borrowed_objects")
    inventory_object = db.relationship('InventoryObject', back_populates="lend_to")


class User_in_Organisation(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    organisation_id = db.Column(db.Integer, db.ForeignKey("organisation.id"), primary_key=True)
    rank_id = db.Column(db.Integer, db.ForeignKey("rank.id"))

    user = db.relationship('User', back_populates="organisations")
    organisation = db.relationship('Organisation', back_populates="user")


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    bio = db.Column(db.String(256))
    organisations = db.relationship("User_in_Organisation", back_populates="user")
    borrowed_objects = db.relationship("Lend_Objects", back_populates="user")

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
        for i in self.organisations:
            if old_organisation.id == i.organisation_id:
                db.session.delete(i)

    """Definiere die Beschreibung für diesen Nutzer"""
    def set_bio(bio):
        if len(bio) <= 256:
            self.bio = bio


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Organisation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    description = db.Column(db.String(256))
    user = db.relationship("User_in_Organisation", back_populates="organisation")
    inventoryobjects = db.relationship('InventoryObject', backref='owner', lazy=True)
    statuses = db.relationship('Status', backref='from_organisation', lazy=True)
    categorys = db.relationship('Category', backref='from_organisation', lazy=True)
    ranks = db.relationship('Rank', backref='from_organisation', lazy=True)

    """URL der Profilseite"""
    def page(self):
        return url_for('organisation', organisation=self.name)

    """Anzahl registrierter Nutzer"""
    def user_count(self):
        return len(self.user)

    """Füge einen Nutzer hinzu"""
    def add_user(self, user):
        for i in self.user:
            if i.user_id == user.id:
                return False
        a = User_in_Organisation()
        a.user = user
        a.organisation = self

    """Entferne einen Nutzer"""
    def remove_user(self, old_user):
        for i in self.user:
            if old_user.id == i.user_id:
                db.session.delete(i)

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


    """Nimm einen Gegenstand zurück"""
    def take_back_object(self, object):
        assert object in self.inventoryobjects, "Object not owned by organisation"
        assert object.lend_to is not None, "Object is not lent to a user"
        # success
        object.lend_to = None

    """Füge eine Kategorie hinzu"""
    def add_category(self, category):
        if not category in self.categorys:
            self.categorys.append(category)

    """Füge einen Rang hinzu"""
    def add_rank(self, rank):
        if not rank in self.ranks:
            self.ranks.append(rank)

    """Gebe einem User einen Rang"""
    def set_rank(self, user, rank):
        for i in self.user:
            if i.user_id == user.id:
                i.rank = rank

    """Erfahre den Rang eines Nutzers"""
    def get_rank(self, user):
        for i in self.user:
            if i.user_id == user.id:
                return i.rank

    """Definiere die Beschreibung für die Organisation"""
    def set_description(self, desc):
        if len(desc) <= 256:
            self.description = desc


class InventoryObject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    article = db.Column(db.String(64), index=True)
    organisation = db.Column(db.Integer, db.ForeignKey('organisation.id'))
    description = db.Column(db.String(256))
    room = db.Column(db.Integer, db.ForeignKey('room.id'))
    status = db.Column(db.Integer, db.ForeignKey('status.id'))
    categorys = db.relationship('Category', secondary=category_inventoryobject, back_populates='inventoryobjects')
    lend_to = db.relationship("Lend_Objects", back_populates="inventory_object")

    """Ordne Gegenstand einem Raum/Ort zu"""
    def set_room(self, room):
        self.room = room.id

    """Ordne einem Gegenstand einen Zustand zu"""
    def set_status(self, status):
        if self.organisation == status.organisation:
            self.status = status.id

    """Füge einem Gegenstand eine Kategorie zu"""
    def add_category(self, category):
        if self.organisation == category.organisation:
            self.categorys.append(category)

    """Definiere die Beschreibung für das Objekt"""
    def set_description(self, desc):
        if len(desc) <= 256:
            self.description = desc


class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    description = db.Column(db.String(128))
    inventoryobjects = db.relationship('InventoryObject', backref='in_room', lazy=True)

    """Definiere die Beschreibung für diesen Raum"""
    def set_description(desc):
        if len(desc) <= 128:
            self.description = desc


class Status(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    description = db.Column(db.String(128))
    inventoryobjects = db.relationship('InventoryObject', backref='has_status', lazy=True)
    organisation = db.Column(db.Integer, db.ForeignKey('organisation.id'))

    """Definiere die Beschreibung für diesen Zustand"""
    def set_description(desc):
        if len(desc) <= 128:
            self.description = desc


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    description = db.Column(db.String(128))
    organisation = db.Column(db.Integer, db.ForeignKey('organisation.id'))
    inventoryobjects = db.relationship('InventoryObject', secondary=category_inventoryobject, back_populates='categorys')

    """Definiere die Beschreibung für diesen Zustand"""
    def set_description(desc):
        if len(desc) <= 128:
            self.description = desc


class Rank(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    description = db.Column(db.String(128))
    # Berechtigungen gerne einfügen
    example = db.Column(db.Boolean)

    organisation = db.Column(db.Integer, db.ForeignKey('organisation.id'))
    user = db.relationship('User_in_Organisation', backref='rank', lazy=True)

    """Definiere die Beschreibung für diesen Rang"""
    def set_description(desc):
        if len(desc) <= 128:
            self.description = desc
