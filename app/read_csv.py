import csv

# Let's gooooo
"""Daten einlesen"""
def read_the_file(document):
    with open(document) as file:
        read = csv.reader(file, delimiter=';')
        data = []
        for row in read:
            # Auswahl der richtigen Datenreihen
            if row[0] and row[1] and not row[0] == "Artikel":
                # Umgehen von so ner Excel Sache in unserer Inventurliste
                if row[5] == '0':
                    row[5] = '/'
                # Da es "Überkategorien" gibt: Diese noch der Kategorie"spalte" hinzufügen
                x = row[4]
                row[4] = []
                row[4].append(kat)
                row[4].append(x)
                # Zeile der Datenliste hinzufügen
                data.append(row)
            elif row[0]:
                # Wenn es keine richtige Datenzeile ist, bedeutet das, dass hier eine Oberkategorie steht - wird hiermit eingelesen
                kat = row[0]
    return data

"""Alle Kategorien der Daten ermitteln"""
def get_categories(ind, data):
    categories = []
    for i in data:
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
def get_status(ind, data):
    status = []
    for i in data:
        if not i[ind] in status:
            status.append(i[ind])
    return status
