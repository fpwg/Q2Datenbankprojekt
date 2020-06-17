from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask import url_for
from datetime import datetime

from flask_login import UserMixin


category_inventoryobject = db.Table('category_organisation',
    db.Column('category_id', db.Integer, db.ForeignKey('category.id'), primary_key=True),
    db.Column('inventoryobject_id', db.Integer, db.ForeignKey('inventory_object.id'), primary_key=True)
)


class Lend_Objects(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    inventory_object_id = db.Column(db.Integer, db.ForeignKey("inventory_object.id"), primary_key=True)
    start_timestamp = db.Column(db.DateTime, default=datetime.utcnow, primary_key=True)
    end_timestamp = db.Column(db.DateTime)

    user = db.relationship('User', back_populates="borrowed_objects")
    inventory_object = db.relationship('InventoryObject', back_populates="lend_to")


class User_in_Organisation(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    organisation_id = db.Column(db.Integer, db.ForeignKey("organisation.id"), primary_key=True)
    rank_id = db.Column(db.Integer, db.ForeignKey("rank.id"))

    user = db.relationship('User', back_populates="organisations")
    organisation = db.relationship('Organisation', back_populates="user")
    rank = db.relationship('Rank', back_populates='user')


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


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Organisation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    description = db.Column(db.String(256))

    user = db.relationship("User_in_Organisation", back_populates="organisation")
    inventoryobjects = db.relationship('InventoryObject', back_populates='organisation')
    statuses = db.relationship('Status', back_populates='organisation')
    categories = db.relationship('Category', back_populates='organisation')
    ranks = db.relationship('Rank', back_populates='organisation')

    """URL der Profilseite"""
    def page(self):
        return url_for('organisation', name=self.name)

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
        assert not object.currently_lend(), "Object is already lent to a user"
        # success
        a = Lend_Objects()
        a.user = user
        a.inventory_object = object

    """Nimm einen Gegenstand zurück"""
    def take_back_object(self, object):
        assert object in self.inventoryobjects, "Object not owned by organisation"
        assert object.currently_lend(), "Object is not lent to a user"
        # success
        object.lend_to[0].end_timestamp=datetime.utcnow()

    """Füge eine Kategorie hinzu"""
    def add_category(self, name):
        if not any(x.name == name for x in self.categories):
            self.categories.append(Category(name=name))

    """Entferne eine Kategorie (sie wird dabei gelöscht)"""
    def remove_category(self, category):
        if category.organisation_id == self.id:
            db.session.delete(category)

    """Füge einen Rang hinzu"""
    def add_rank(self, name):
        if not any(x.name == name for x in self.ranks):
            self.ranks.append(Rank(name=name))

    """Entferne einen Rang (er wird dabei gelöscht)"""
    def remove_rank(self, rank):
        if rank.organisation_id == self.id:
            db.session.delete(rank)

    """Füge einen Zustand hinzu"""
    def add_status(self, name):
        if not any(x.name == name for x in self.statuses):
            self.statuses.append(Status(name=name))

    """Entferne einen Zustand (er wird dabei gelöscht)"""
    def remove_status(self, status):
        if status.organisation_id == self.id:
            db.session.delete(status)

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
    description = db.Column(db.String(256))

    organisation_id = db.Column(db.Integer, db.ForeignKey('organisation.id'), nullable=False)
    organisation = db.relationship("Organisation", back_populates="inventoryobjects")

    room_id = db.Column(db.Integer, db.ForeignKey('room.id'))
    room = db.relationship('Room', back_populates='inventoryobjects')

    status_id = db.Column(db.Integer, db.ForeignKey('status.id'))
    status = db.relationship('Status', back_populates='inventoryobjects')

    categories = db.relationship('Category', secondary=category_inventoryobject, back_populates='inventoryobjects')
    lend_to = db.relationship("Lend_Objects", back_populates="inventory_object")

    """Ordne Gegenstand einem Raum/Ort zu"""
    def set_room(self, room):
        room.inventoryobjects.append(self)

    """Ordne einem Gegenstand einen Zustand zu"""
    def set_status(self, status):
        if self.organisation_id == status.organisation_id:
            status.inventoryobjects.append(self)

    """Füge einem Gegenstand eine Kategorie zu"""
    def add_category(self, category):
        if self.organisation_id == category.organisation_id:
            category.inventoryobjects.append(self)

    """Prüfe, ob ein Gegenstand aktuell verliehen ist"""
    def currently_lend(self):
        if self.lend_to[-1:] and not self.lend_to[-1:][0].end_timestamp:
            return True
        return False

    """Ermittle, welche Person gerade den Gegenstand ausgeliegen hat"""
    def currently_lend_to(self):
        if self.currently_lend():
            return self.lend_to[-1].user


class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    description = db.Column(db.String(128))

    inventoryobjects = db.relationship('InventoryObject', back_populates='room')


class Status(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    description = db.Column(db.String(128))

    organisation_id = db.Column(db.Integer, db.ForeignKey('organisation.id'), nullable=False)
    organisation = db.relationship('Organisation', back_populates='statuses')

    inventoryobjects = db.relationship('InventoryObject', back_populates='status')


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    description = db.Column(db.String(128))

    organisation_id = db.Column(db.Integer, db.ForeignKey('organisation.id'), nullable=False)
    organisation = db.relationship('Organisation', back_populates='categories')

    inventoryobjects = db.relationship('InventoryObject', secondary=category_inventoryobject, back_populates='categories')


class Rank(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    description = db.Column(db.String(128))

    delete_organisation = db.Column(db.Boolean)
    grant_ranks = db.Column(db.Boolean)
    add_users = db.Column(db.Boolean)
    edit_organisation = db.Column(db.Boolean)
    lend_objects = db.Column(db.Boolean)

    organisation_id = db.Column(db.Integer, db.ForeignKey('organisation.id'), nullable=False)
    organisation = db.relationship('Organisation', back_populates='ranks')

    user = db.relationship('User_in_Organisation', back_populates='rank')

    @staticmethod
    def make_admin_rank(name):
        return Rank(name=name, delete_organisation=True, grant_ranks=True, add_users=True, edit_organisation=True, lend_objects=True)