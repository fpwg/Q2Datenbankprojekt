import csv
from app import db
from app.models import Room

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

"""Index der unterschiedlichen Spaltentypen ermitteln -> return article, room, status, category, count, description"""
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
        data.remove(row)
        return data, article, room, status, category, count, description

"""Einfügen der Räume in die Datenbank"""
def put_rooms_into_database(rooms):
    db_rooms = Room.query.all()
    #new_rooms = []
    for i in rooms:
        if not any(x.name == i for x in db_rooms):
            db.session.add(Room(name=i))
            #new_rooms.append(room(name=i))
    #return new_rooms


"""Einlesen einer Datei und einpflegen in die Datenbank"""
def put_filecontents_into_database(document):
    data = read_the_file(document)
    data, article_ind, room_ind, status_ind, category_ind, count_ind, description_ind = get_indexes(data)
    categories = get_categories(category_ind, data)
    rooms = get_rooms(room_ind, data)
    statuses = get_statuses(status_ind, data)

    put_rooms_into_database(rooms)
