![Domainhunter Logo](/Code/WIP/logo1.png "Domainhunter Logo")
# Softwareprojekt 2020: Domain Hunter

Domainhunter ist ein Expertentool, welches eine Menge an Domains überwacht und Hinweise über mögliches Domain-Hijacking geben kann.
Dabei werden periodisch die DNS Metadaten der enthaltenen Domains wie: A, AAAA, NS, MX und TEXT Records und die whois Informationen der zugehörigen IP Adressen aufgelöst, gespeichert und letztlich durch ein Scoring-Algorithmus bewertet.

Der Scoring-Algorithmus wertet hierbei die Art, Menge, sowie das Ausmaß der Veränderung aus und berechnet einen Scoring Wert im Bereich 0-10. Die Höhe des Scoring Wertes gibt hierbei Aufschluss, wie hoch die Wahrscheinlichkeit eines möglichen Domain Hijackings zum Zeitpunkt der Domain Abfrage ist.

_Dies ist das Git-Repository fuer das Softwareprojekt Domain-Hunter. Die initiale Projektbeschreibung liegt unter [projektbeschreibung](projektbeschreibung/)._

## Projektvorstellung

**Elevator Pitch:**
![](/Media/elevator_pitch.mp4 "")

**Ausführlichere Version:**
![](/Media/vorstellung_projekt.mp4 "")

## Inhalt
* [CLI](#cli)
* [Query Menu](#query-menu)
* [Scheduler](#scheduler)
* [Reporting](#reporting)
* [Importing](#importing)
* [Status](#status)
* [Comment and Category Menu](#comment-and-category-menu)
* [Scorer](#scorer)
* [Systemzugriff](#systemzugriff)
* [Externe Ressourcen](#externe-ressourcen)

## CLI

![Main Menu](/Media/cli_menu.png "CLI")

Das Hauptmenü des Systems wird über ein Command Line Interface dargestellt (CLI) dargestellt.
Die einzelnen Funktionen werden dabei über die jeweilige Zahl des zugehörigen Elements angesteuert.
Die Titelleiste, in diesem Fall "Main menu" zeigt das aktuelle Navigationsmenü an.

* Mit den Zahlen 1-6 werden also die Menüeinträge ausgewählt und auf die entsprechende Seite gesprungen
* Mit "p" wird in das vorherige Menü gesprungen 
* Mit "x" wird das System beendet.

## Query Menu

Über das Query-Menu können spezielle, benutzerdefinierte Abfragen durchgeführt werden.

![Query Menu](/Media/query_menu.png "Query Menu")

Erläuterung zu den Menüpunkten:
* Eintrag "1": Domainabfrage ohne Scheduler zu einer beliebigen Domain starten
* Eintrag "2": Subdomainfinder ohne Importer zu einer Domain starten

## Scheduler

Der Scheduler verwaltet die gesamte Reihenfolgebildung und Auswahl der Domains. Einmal gestartet, läuft der Scheduler mit seinen Prozessen im Hintergrund und fragt anhand der definierten Warte- und Updateparameter alle Domains ab. 
Der Abfrageprozess beinhaltet dabei die Folgenden Schritte:
* DNS Abfrage der Records und whois Einträge
* Erstellen einer neuen Domain-Query zum aktuellen Zeitpunkt
* Erfassen der Domain-Query in der Datenbank
* Triggern des [Scorers](#scorer)

![Scheduler Menu](/Media/scheduler_menu.png "scheduler")

Erläuterung zu den Menüpunkten:
* Eintrag "1": Startet den Scheduler mit den Standardparametern (Wait time = 5 min, Update time = 1440 min)
* Eintrag "2": Stoppt den Scheduler
* Eintrag "3": Wait time einstellen
* Eintrag "4": Update time einstellen

***Wait time:*** Speichert wie lange nach leeren von nextFQDNs gewartet werden soll, um nach neuen zu aktualisierenden Domains zu suchen.

***Update time:*** Speichert wie häufig eine Domain aktualisiert werden soll.

## Reporting

Über das Reporting Menu können benutzerdefinierte Reports zu Einzeldomains oder über die gesamte Datenbank erzeugt werden. Der Report kann dabei auf verschiedene Weise erzeugt werden und durch mehrere Filter angepasst werden.

Report Ausgabevarianten sind dabei:
* CLI-interne Ausgabe
* CSV Export
* PDF Export

![Reporting Menu](/Media/reporting_menu.png "Reporting Menu")

Erläuterung zu den Menüpunkten:
* Eintrag "1": Report zu einer einzigen Domain ohne Filter erstellen
* Eintrag "2": Benutzerdefinierter Report mit Filter erstellen

Filtermöglichkeiten:

![Filters](/Media/reporting_filters.png "Filters")

In dieser Ansicht werden sämtliche Filteroptionen dargestellt. Die aktuelle Filterauswahl wird dabei jederzeit mittig angezeigt.

**Video zum Filtermenü:**

![](/Media/filter_video.mp4 "")

Anhand der eingestellten Filter wird eine Datenbank-Abfrage ausgeführt.
Das Ergebnis der Abfrage kann vom System auf folgende Arten exportiert werden:

* PDF Report
* CSV Report
* Terminal-Report

Während der Terminal-Report die Ergebisliste als String darstellt, werden die Ergebnisse bei den Anderen Arten aufbereitet und in eine CSV, oder PDF Datei exportiert.

**Beispielausschnitt eines PDF-Reports:**

![pdf](/Media/pdf_export.png "pdf")

**Beispielausschnitt eines CSV-Reports:**

![csv](/Media/csv_export.png "csv")

**Beispielausschnitt eines Terminal-Reports:**

![console](/Media/console_export.png "console")

## Importing

Über das Importing Menu können neue Domains dem System hinzugefügt werden. Bei Bedarf kann zu den Domains noch ein Subdomainfinder gestartet werden, welcher zu einer gegebenen Domain existierende Subdomains sucht und sie automatisch hinzufügt.

![Importing](/Media/import_menu.png "Importing")

Erläuterung zu den Menüpunkten:
* Eintrag "1": Einzelne Domain importieren
* Eintrag "2": Bulk Import mittels CSV Datei
* Eintrag "3": Menge der zu Überprüfenden Subdomains einstellen (Auswahl zwischen 100, 1000 und 10000 möglichen Subdomains)

_Beachte:_ Die Menge an zu überprüfenden Subdomains beeinträchtigt die Performance.

**Subdomainfinder:**

Der Subdomainfinder wird jeweils (Menüeintrag 1 und 2) über das Anhängen von "-sd" an die domain (1) bzw. den Pfad zur CSV (2) gestartet. Falls nicht anders eingestellt, wird im Standardfall gegen 1000 mögliche Subdomains geprüft und die existierenden Ergebnise werden dann automatisch der Datenbank zugeführt und abgespeichert. 

## Status

Eine Übersicht über den aktuellen Status ist über das Status Menü möglich.
Diese Ansicht wird kontinuierlich aktualisiert und zeigt den Zuwachs an Domains und Abfragen an.

![status_pic](/Media/status_thumbnail.png "Status Bild")

* In der ersten Zeile wird der Status des Schedulers angezeigt.
* Current Domains gibt die Anzahl an aktuell gespeicherten Domains in der Datenbank an
* Current Domainqueries gibt die Anzahl an ausgeführten Abfragen über den Gesamten Zeitraum an.
* Last updated Domain gibt die zuletzt aktualisierte Domain an.

Das folgende Screenvideo zeigt, wie sich die Zeile mit der zuletzt behandelten Domain stetig aktualisiert:

![](/Media/status_menu.mp4 "")

## Comment and Category Menu

Über das Add Domain / Query information Menu können Kommentare und Kategorien zu Domains oder einzelnen Domainqueries zugeordnet werden. Dies ermöglicht es, Anmerkungen zu Vorfällen festzuhalten und benutzerspezifische Kategorien zu vergeben, um im Nachhinein hierüber zu Filtern.

![Category](/Media/category_menu.png "Category")

Erläuterung zu den Menüpunkten:
* Eintrag "1": Kommentar zu einer Domain verwalten
* Eintrag "2": Kommentar zu einer Domain-Query verwalten
* Eintrag "3": Einer Domain-Query eine Kategorie zuweisen

_Beachte:_ Bei der Verwaltung von Kommentaren oder Kategorien zu Queries muss stets zu der Domain auch die Query-Time angegeben werden. Es empfiehlt sich also bereits beim Reporting die gewünschte Query samt Query-Time festzuhalten.

## Scorer

Die Bewertung der Daten, also das "Scoring" wird im Scorer Modul durchgeführt.
Hierbei wird die Datengrundlage zu jeder Domain-Query herangezogen und mit der Vorgänger Domain-Query verglichen.
Der Scoring-Algorithmus rechnet dann einen Wahrscheinlichkeitswert zwischen 1 und 10 aus, welcher ein Indiz für die Wahrscheinlichkeit eines möglichen Domain Hijackings darstellt.

Hierbei werden unterschiedliche Records verschieden stark gewichtet, da das System einzelne Record-Veränderungen als besonders kritisch einstuft.
Das Modell des Scorers funktioniert dabei nach folgendem Prinzip:

Jeder Record wird einzeln betrachtet, dabei wird für jeden Record ein Scoringwert berechnet. Der Scoringwert berechnet sich hierbei aus: **Basiswert * Indikationswert**. Die Basiswerte sind dabei wie folgt belegt und basieren auf der Kritikalität bei Veränderung dieses Records:

* **TXT-Record:** 1
* **IPv4** und **IPv6:** 2    
* **MX-Record:** 5
* **NS-Record:** 7

Die Indikationswerte berechnen sich dabei so:

* IPv4 und IPv6: Whois-Eigenschaften vergleichen:
	- Verändert sich die Person, kann das gewöhnlich sein -> niedriger Indikationswert
	- Verändert sich z.B. Das Land ist das ungewöhnlich -> hoher Indikationswert
	- Verändert sich Person oder Organisation ist dies eher ungewöhnlich -> hoher Indikationswert
* MX- und NS-Record: Hostnamen vergleichen
	- Übliche Fälle:
	- Der neue NS Host Name liegt in der Second-Level-Domain (SLD) (zB.: NS1.**w-hs**.de-> NS2.**w-hs**.de für die Domain w-hs.de)
	- Der neue NS Host Name liegt nicht in der SLD, jedoch in der gleichen wie in der vorherigen Domain-Query (zB.: dns-1.**dfn**.de -> dns-2.**dfn**.de für die Domain w-hs.de)

Der zum Schluss höchste Einzelwert eines Records wird nach der Berechnung dann der finale Score für die Domain-Query und wird in der Datenbank persistiert.

## Systemzugriff

### Server
Der Server ist unter dem Hostname `domainhunter.if-is.net` per SSH erreichbar.

* Hostname: `domainhunter.if-is.net`
* Username: `fu`

Bisherige SSH-Keys sind dort bereits eingetragen, sodass Sie sich per SSH-Key einloggen koennen (Anleitung: https://www.heise.de/tipps-tricks/SSH-Key-erstellen-so-geht-s-4400280.html). Auf der Kommandozeile eines Linux-Systems beispielsweise:
```sh
$ ssh fu@domainhunter.if-is.net
Last login: Tue Sep  1 10:46:13 2020
[fu@domainhunter ~]$
```
Wenn Sie sich auf dem Host einloggen, muessen Sie die virtuelle Umgebung aktivieren, das geht mit dem Befehl `source ~/.venv/domainhunter/bin/activate` so:
source ~/.venv/domainhunter/bin/activate
```sh
[fu@domainhunter ~]$ source ~/.venv/domainhunter/bin/activate
(domainhunter) [fu@domainhunter ~]$
```

`pip list` zeigt, welche Pakete gerade alle installiert sind:
```sh
(domainhunter) [fu@domainhunter ~]$ pip list
Package    Version
---------- -------
dnspython  2.0.0
pip        20.2.4
psycopg2   2.8.4
setuptools 41.6.0
(domainhunter) [fu@domainhunter ~]$
```

### Datenbank
Sie erhalten Zugriff auf eine PostgreSQL-Datenbank des Instituts fuer Internet-Sicherheit. Die Datenbank ist nur von dem Server aus erreichbar. Die Zugangsdaten sind wie folgt:

* Datenbankname: `domainhunter` (sowie zu Testzwecken `domainhunter_test`)
* Hostname: `ifisdb.if-is.net`
* Username: `domainhunter`
* Passwort: `bR2X4RKcd3uIybFT`

Der Zugriff per Kommandozeile auf die Datenbank geht beispielsweise wie folgt von dem Server aus (eingeloggt als `fu@domainhunter.if-is.net`):

```sh
[fu@domainhunter ~]$ psql -h ifisdb.if-is.net -U domainhunter domainhunter
Password for user domainhunter:
psql (12.4, server 12.3)
Type "help" for help.

domainhunter=>
```

Mit dem Kommando `\d+` koennen Sie sich die Datenbankelemente (Tabellen, Views, etc.) anzeigen lassen. Bisher ist Ihre Datenbank komplett leer. Sie koennen und muessen sich ueberlegen, welche Tabellen Sie anlegen und wie Sie sie verknuepfen, fuellen und nutzen. Die Dokumentation von PostgreSQL ist wirklich klasse. Informationen zum `psql`-Client finden Sie z.B. hier: https://www.postgresql.org/docs/12/app-psql.html.

### Screen

Um das Programm auch beim trennen der SSH Session im Hintergrund laufen zu lassen, werden mit dem Programm Screen Sessions erstellt. Hier eine kurze Anleitung: 

Die  wichtigsten Befehle bzw. Tastenkombinationen, die man kennen sollte, sind:

Strg + A , gefolgt von  Leertaste zum Wechseln zwischen den einzelnen Fenstern einer Sitzung

Strg + A , gefolgt von D zum Trennen (detach) der Verbindung zur aktuellen Sitzung, die Sitzung läuft dann im Hintergrund weiter

Starten einer neuen Sitzung mit dem Namen "sitzung1" (siehe auch Unterschied zwischen Sitzung und Fenster):

`screen -S sitzung1`
 
Trennt (engl.: "detach") die Verbindung zur aktuellen Sitzung: Strg + A + D


Nimmt die Sitzung mit dem Namen "sitzung1" wieder auf:

`screen -r sitzung1`

Auflisten der Namen aller laufenden Screen-Sitzungen:

`screen -ls `

Die Sitzung mit dem Namen "sitzung1" kann an mehreren Computern gleichzeitig angezeigt werden:

`screen -rx sitzung1 `

Mehr Deetails in der [Screen Wiki](https://wiki.ubuntuusers.de/Screen/)

## Externe Ressourcen
* [CrowdStrike Domain Hijacking Blog Post](https://www.crowdstrike.com/blog/widespread-dns-hijacking-activity-targets-multiple-sectors/)
* [RiskIQ PassiveTotal](https://community.riskiq.com/search/mail.apc.gov.ae/domaincertificates)
* [Thesis Template (Abschlussarbeit-Vorlage)](https://gitlab.internet-sicherheit.de/cdietric/thesis-template)
