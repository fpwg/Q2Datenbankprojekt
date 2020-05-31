import csv
from app import db
from app.models import Room, Category, Status, InventoryObject

"""Daten einlesen"""
def read_the_file(document):
    with open(document) as file:
        read = csv.reader(file, delimiter=';')
        data = []
        for row in read:
            # Auswahl von Reihen mit Inhalt
            if row[0] and row[1]:
                # Umgehen von so ner Excel Sache in (unserer) Inventurliste
                if row[5] == '0':
                    row[5] = '/'
                # Wenn es "Überkategorien" gibt: Diese noch der Kategorie"spalte" hinzufügen
                if kat and data:
                    x = row[4]
                    row[4] = []
                    row[4].append(kat)
                    row[4].append(x)
                # Zeile der Datenliste hinzufügen
                data.append(row)
            elif row[0]:
                # Wenn es keine richtige Datenzeile ist, bedeutet das, dass hier eine Oberkategorie steht - wird hiermit erkannt
                kat = row[0]
    return data

"""Alle Kategorien der Daten ermitteln"""
def get_categories(ind, data):
    categories = []
    for i in data:
        if type(i[ind]) is list:
            for j in i[ind]:
                if not j in categories:
                    categories.append(j)
    return categories

"""Alle Orte der Daten ermitteln"""
def get_rooms(ind, data):
    rooms = []
    for i in data:
        if not i[ind] in rooms:
            rooms.append(i[ind])
    return rooms

"""Alle Zustände der Daten ermitteln"""
def get_statuses(ind, data):
    status = []
    for i in data:
        if not i[ind] in status:
            status.append(i[ind])
    return status

"""Index der unterschiedlichen Spaltentypen ermitteln -> return data (ohne Beschreibungszeile), indexes -> [article, room, status, category, description, count]"""
def get_indexes(data):
    article = -1
    room = -1
    status = -1
    category = -1
    count = -1
    description = -1
    row = [x.casefold() for x in data[0]]
    if "artikel".casefold() in row or "article".casefold() in row:
        for i in row:
            if i == "artikel".casefold() or i == "article".casefold():
                article = row.index(i)
            if i == "room".casefold() or i == "raum".casefold() or i == "ort".casefold():
                room = row.index(i)
            if i == "status".casefold() or i == "zustand".casefold() or i == "funktion".casefold():
                status = row.index(i)
            if i == "category".casefold() or i == "kategorie".casefold():
                category = row.index(i)
            if i == "anzahl".casefold() or i == "count".casefold():
                count = row.index(i)
            if i == "bemerkung".casefold() or i == "beschreibung".casefold() or i == "description".casefold():
                description = row.index(i)
        data.remove(data[0])
        indexes = [article, room, status, category, description, count]
        return data, indexes

"""Einfügen der Räume in die Datenbank (+ wenn auskommentierte Sachen eingefügt werden return der neu eingefügten Räume)"""
def put_rooms_into_database(rooms):
    db_rooms = Room.query.all()
    #new_rooms = []
    for i in rooms:
        if not any(x.name == i for x in db_rooms):
            r = Room(name=i)
            db.session.add(r)
            #new_rooms.append(r)
    #return new_rooms

"""Einfügen der Kategorien in die Datenbank (+ wenn auskommentierte Sachen eingefügt werden return der neu eingefügten Kategorien)"""
def put_categories_into_database(categories, organisation):
    #new_categories = []
    for i in categories:
        if not any(x.name == i for x in organisation.categorys):
            c = Category(name=i)
            organisation.add_category(c)
            #new_categories.append(c)
    #return new_categories

"""Einfügen der Zustände in die Datenbank (+ wenn auskommentierte Sachen eingefügt werden return der neu eingefügten Zustände)"""
def put_statuses_into_database(statuses, organisation):
    #new_statuses = []
    for i in statuses:
        if not any(x.name == i for x in organisation.statuses):
            s = Status(name=i)
            organisation.add_status(s)
            #new_statuses.append(s)
    #return new_statuses

"""Erstellen der einzufügenden Objekte"""
def create_object(article_list, organisation, rooms, statuses, categories, indexes):
    # Objekt
    inv = InventoryObject(article=article_list[indexes[0]], organisation=organisation.id)
    # Raum
    for j in rooms:
        if j.name == article_list[indexes[1]]:
            inv.set_room(j)
    # Zustand
    for j in statuses:
        if j.name == article_list[indexes[2]]:
            inv.set_status(j)
    # Kategorien
    for x in article_list[indexes[3]]:
        for j in categories:
            if j.name == x:
                inv.add_category(j)
    # Beschreibung
    inv.set_description(article_list[indexes[4]])

    return inv

"""Einfügen der Objekte in die Datenbank"""
def put_object_into_database(data, indexes, organisation):
    rooms = Room.query.all()
    statuses = Status.query.all()
    categories = Category.query.all()
    for i in data:
        if i[indexes[5]].isnumeric():
            for y in range(int(i[indexes[5]])):
                db.session.add(create_object(article_list=i, organisation=organisation, rooms=rooms, statuses=statuses, categories=categories, indexes=indexes))
        else:
            inv = create_object(article_list=i, organisation=organisation, rooms=rooms, statuses=statuses, categories=categories, indexes=indexes)

            desc = i[indexes[4]], "count: ", i[indexes[5]]
            inv.set_description(i[indexes[4]])

            db.session.add(inv)

"""Einlesen einer Datei und einpflegen in die Datenbank"""
def put_filecontents_into_database(document, organisation):
    data = read_the_file(document)
    data, indexes = get_indexes(data)
    if indexes[3] > -1:
        categories = get_categories(indexes[3], data)
        put_categories_into_database(categories, organisation)
    if indexes[1] > -1:
        rooms = get_rooms(indexes[1], data)
        put_rooms_into_database(rooms)
    if indexes[2] > -1:
        statuses = get_statuses(indexes[2], data)
        put_statuses_into_database(statuses, organisation)
    put_object_into_database(data, indexes, organisation)
