"""
#import Domain

def importfromtxt(pfad, findSubdomain=True):
    #Importiert Domains von einer TXT Datei.
    #Der 1.Paramter ist der vollstaendigen Pfad der TXT Datei.
    #Der 2.Paramter gibt an, ob nach Subdomains gesucht werden soll.
    #(Standartmaesig wird nach Subdomains gesucht)

    domains = []
    try:
       #pfad = "C:\\Users\\i\\Desktop\\python\\test.txt"
       datei = open(pfad, "r")
       for zeile in datei:
           liste = zeile.split(",")
           for i in liste:
               domains.append(i.strip())
    except FileNotFoundError:
        print("Die Datei existiert nicht")
    except:
        print("Es ist ein Fehler beim Zugriff / Lesen der Datei aufgetreten.")
    finally:
        datei.close()
    #TODO Mit domain-liste domain-objekte erzeugen
"""
#TODO:Domain objekte erstellen
#def erstelle_Domain(domain, findSubdomain):

import csv
def importfromcsv(pfad, findSubdomain=True):
    """Importiert Domains von einer CSV Datei.
    Der 1.Paramter ist der vollstaendigen Pfad der CSV Datei.
    Der 2.Paramter gibt an, ob nach Subdomains gesucht werden soll.
    (Standartmaesig wird nach Subdomains gesucht)
    """

    domains = []
    pfad = "C:\\Users\\i\\Desktop\\python\\top-1m.csv"
    with open(pfad) as csvdatei:
        csv_reader_object = csv.reader(csvdatei)

        for row in csv_reader_object:
            #spziell hier:  1,google.de deswegen Zugriff auf Indize 1
            domains.append(row[1])
        print(len(domains))

importfromcsv("")
