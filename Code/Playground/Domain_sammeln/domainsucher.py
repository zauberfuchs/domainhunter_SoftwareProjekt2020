import csv
import os
import random
import time
from urllib.parse import urlparse
from googlesearch import search

menge = set()  # Menge von interessanten Domains
countrydic = {}  # Woerterbuch von ccTLD zu Laendernamen
agencydic = {}  # Woerterbuch von ccTLD/.org-TLD zu Liste von Geheimdiensten/Organisationen


def googlen(query, max_ergebnis, wartezeit):
    gefundene_domains = []
    for i in search(query, tld="com", num=10, stop=max_ergebnis, pause=wartezeit):
        # i = http://www.example.test/
        i = urlparse(i).netloc
        # i = www.example.test
        parts = i.split(".")
        if parts[0] == "www":
            i = ".".join(parts[1:])
        # i = example.test
        gefundene_domains.append(i)

    try:
        if os.path.exists('.google-cookie'):
            os.remove('.google-cookie')
    except Exception:
        pass
    return gefundene_domains


def protokolliere(query, gefundene_domains, ausgewaehlte_domains):
    print("Gesucht: " + query)
    print(f"gefundene Domains: {gefundene_domains}")
    print("ausgewählte Domains: " + str(set(ausgewaehlte_domains)) + "\n")

    global protokoll
    protokoll = protokoll + "Gesucht: " + query + "\n" + f"gefundene Domains: {gefundene_domains}\n" + "ausgewählte Domains: " + str(set(ausgewaehlte_domains)) + "\n\n"


def entscheide(domain, tld):

    if tld == ".org":
        if domain.split(".")[-2] == "wikipedia":
            return False

    if domain.endswith(tld):
        return True
    else:
        return False


def finde_gov_domains():
    # countrydic Dictionary auffuellen
    try:
        # Quelle von country.txt : https://simple.wikipedia.org/wiki/List_of_Internet_top-level_domains
        datei = open("country.txt", "r")
        for zeile in datei:
            liste = zeile.split()
            countrydic[liste[0]] = liste[1].replace("-", " ")
    except FileNotFoundError:
        print("Die Datei existiert nicht")
    finally:
        datei.close()

    cctld_list = countrydic.keys()
    for cctld in cctld_list:
        country = countrydic[cctld]

        suchbegriff1 = country + " gov"
        suchbegriff2 = country + " ministry of"

        suchergbenisse1 = googlen(suchbegriff1, 10, int(random.uniform(5, 15)))
        suchergbenisse2 = googlen(suchbegriff2, 10, int(random.uniform(5, 15)))

        if cctld == ".us":
            cctld = ".gov"

        auswahl1 = []
        for ergebnis in suchergbenisse1:
            if entscheide(ergebnis, cctld):
                auswahl1.append(ergebnis)

        auswahl2 = []
        for ergebnis in suchergbenisse2:
            if entscheide(ergebnis, cctld):
                auswahl2.append(ergebnis)

        for item in auswahl1:
            menge.add(item)
        for item in auswahl2:
            menge.add(item)

        protokolliere(suchbegriff1, suchergbenisse1, auswahl1)
        protokolliere(suchbegriff2, suchergbenisse2, auswahl2)


def finde_geheimdienst_domains():
    """Finde Geheimdienst- und Organisation-Domains"""
    # Quelle
    # https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=&ved=2ahUKEwjhisKdgsztAhUF66QKHUVOACsQFjAMegQIIxAC&
    # url=https%3A%2F%2Flink.springer.com%2Fcontent%2Fpdf%2Fbbm%253A978-3-8348-8640-8%252F1.pdf&usg=AOvVaw1WlgYlSqO4gvbd_Ijvs0Du

    # agencydic Dictionary auffuellen
    try:
        datei = open("organisationen.txt", "r")
        for zeile in datei:
            liste = zeile.split()
            cctld = liste[0]
            agency = " ".join(liste[1:])

            if agencydic.get(cctld) is None:
                agencydic[cctld] = [agency]
            else:
                val = agencydic.get(cctld)
                val.append(agency)
                agencydic[cctld] = val
    except FileNotFoundError:
        print("Die Datei existiert nicht")
    finally:
        datei.close()

    for tld in agencydic.keys():
        geheimdienstliste = agencydic[tld]
        for geheimdienst in geheimdienstliste:
            suchergbenisse = googlen(geheimdienst, 10, int(random.uniform(5, 15)))

            if tld == ".us":
                tld = ".gov"

            auswahl = []
            for i in suchergbenisse:
                if entscheide(i, tld):
                    auswahl.append(i)
            protokolliere(geheimdienst, suchergbenisse, auswahl)
            for item in auswahl:
                menge.add(item)


def erstelle_protokolltxt():
    """Erstellt ein Protokoll.txt, wo alle Ausgaben des Programms reingeschrieben wird."""
    f = open("Protokoll.txt", "w")
    f.write(protokoll)
    f.close()


def erzeugecsv():
    """Erzeugt eine CSV mit den ausgewaehlten Domains"""

    with open('interessante_domains.csv', 'w', newline='') as csvfile:
        domainwriter = csv.writer(csvfile)
        for i in menge:
            domainwriter.writerow([i])


print("Start: " + time.asctime())
protokoll = "Start: " + time.asctime() + "\n"  # Ausgabeprotokoll

try:
    # finde_gov_domains()
    finde_geheimdienst_domains()
except Exception:
    print("Ein Fehler ist aufgetreten. ")
    protokoll = protokoll + "Ein Fehler ist aufgetreten. \n"

print("Ende: " + time.asctime())
protokoll = protokoll + "Ende: " + time.asctime() + "\n"

erzeugecsv()
erstelle_protokolltxt()
