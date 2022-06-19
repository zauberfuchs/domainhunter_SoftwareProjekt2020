# 1.    Projektbeschreibung
## 1.1 Einführung
Das zu erstellende Softwaresystem im folgenden Domain Hunter (DH) genannt ist ein datenbankbasiertes Analyse Tool und dient zur Feststellung von Veränderungen in DNS Einträgen und dem Auffinden ungewöhnlicher DNS Veränderungen. Eine ungewöhnlicher DNS Veränderungen kann auf ein Domain Hijacking (die unberechtigte Übernahme einer Domain) hinweisen. Das Auffinden von Domain Hijacking soll durch DH beschleunigt und vereinfacht werden. 

##  1.2 Projektumfeld
Das Projekt wird im Rahmen eines Bachelor Studiums als Software-Projektes (SPIN / SPMI / SPWI, 4./5. Fachsemester) durchgeführt.
Die Betreuung erfolgt durch Prof. Dr. Christian J. Dietrich (Prof. Dietrich).
An der Realisierung arbeiten:
- Michael Kalamarski
- Nico Hegemann
- Julien Förderer 
- Ibrahim Cevik
- Arne Thiel

.
## 1.3 Schnittstellen
Die Projektgruppe kommuniziert direkt mit Prof. Dietrich, Corona bedingt allerdings vornehmlich per Mail oder Videokonferenz. Zusätzlich kommt eine Gitlab Instanz zum Einsatz um Dateien oder Aufgaben untereinander oder mit Prof. Dietrich auszutauschen. 

## 1.4 Ist-Analyse
Aktuell liegt am if(is) noch kein vergleichbares Produkt vor. Außerhalb des if(is) gibt es durchaus vergleichbare kommerzielle und wissenschaftliche Projekte. Z.B. Analysiert das LUDIC System der TU Darmstadt Domain Hijacking sogar über verteilte Standorte und damit möglichst viele DNS Server hinweg. Auch Kommerzielle Firmen wie z.B. die RiskIQ, Inc. Haben sich unter anderem auf das Sammeln von DNS Einträgen spezialisiert.  

## 1.5 Soll-Zustand
Das Produkt soll auch über den Projektzeitraum hinweg (und darüber hinaus) nach Möglichkeit produktiv am if(is) eingesetzt werden um die Mitarbeiter auf untersuchenswerte Domain Veränderungen hinzuweisen. Dabei kann das System keine Definitiven Aussagen, es schlägt nur Fälle vor die eine nähere Betrachtung wert sind. Hierdurch soll es den Mittarbeitern des if(is) ermöglicht werden möglichst schnell auf ungewöhnliche DNS Veränderungen zu reagieren und diese Fälle zeitnah weiter zu untersuchen. 

# 2.     Anforderungen
## 2.1 Visionen und Ziele
### /V110/
Durch den Einsatz von DH sollen vermeintliche Fälle von Domain Hijacking erkannt und dokumentiert werden. 
### /Z110/
Dem User soll gemeldet werden, wenn ein vermeintlicher Fall von Domain Hijacking vorliegt
### /Z120/
Auch nicht erkannte Fälle sollen dokumentiert werden um sie ggf. im Nachhinein zu analysieren. 
### /Z130/
Dem User soll es möglich sein einen Kommentar zu einer Domainveränderung zu verfassen.  
### /Z140/
Der User soll Domainveränderungen kategorisieren können.
### /Z150/
Dem User soll es möglich sein alle Domain Veränderungen zu einer bestimmten (Sub)Doamain zu finden. 
### /Z160/
Der User soll einzelne oder auch eine größere Menge (Batchimport) an Domains zur Beobachtung hinzufügen können.
### /Z170/
DH soll den User unterstützen (Sub)Domains zu bestimmen welche beobachtet werden sollten.
### /Z180/
Falls noch Kapazität vorhanden ist soll DH Berichte (z.B. Monatsberichte) per Mail verschicken können.

## 2.2     Rahmenbedingungen
### /R10/
DH ist ein CLI basiertes Analyse Tool
### /R20/
Zielgruppe sind Fachanwender im Bereich der IT Security. 
### /R30/
Das System wird im akademischen Forschungsumfeld eingesetzt.
### /R40/
Der Betrieb der Server und Netzwerk Umgebung des DH Systems obliegt dem if(is) 
### /R50/ 
Die wöchentliche Betriebszeit des Systems muss 150 Stunden betragen 
### /R60/
Es ist mit 100.000 zu überwachenden (Sub)Domains zu rechnen. 
### /R70/
Der Betrieb des Systems muss weitestgehend unbeaufsichtigt ablaufen.
### /R75/
Ausgenommen von /R70/ sind Änderungen am System.
### /R90/
Eine Realisierung der DH Oberfläche erfolgt ausschließlich in der englische Sprache. 
### /R100/
Zur Interaktion mit dem DH System ist eine SSH Verbindung zum DH Server System notwendig.
### /R110/
Eine GUI Version ist nicht Bestandteil des Projekts. Kann aber in einem Folgeprojekt realisiert werden. 
### /R110/
Eine Mobile/Smartphone optimierte Version ist nicht Bestandteil des Projekts 
### /R130/
Netzwerkverbindung des DH Servers zum WWW und Datenbank Server und die benötigten Ports sind:
DH-Server> Internet: 53, 853 ggf. 443 (DoH)
DH-Server> Gitlab: TBD
DH-Server-> DB-Server: TBD
### /R140/
Der DH Server ist aus dem Internet von den Clients zu erreichen.
Internet -> DH: Port 22
### /R150/
Die Entwicklungsumgebung kann identisch mit der Zielumgebung sein.

## 2.3    Kontext und Überblick
### /K10/
User greifen über das Internet oder das LAN per ssh auf DH zu. 
### /K20/
DH greift auf die öffentliche DNS Infrastruktur zu. Welcher Server genau hier verwendet werden sollen wird im Rahmen des Projekts bestimmt.
### /K25/
DH soll Domain Hijacking auffinden welches über die legitime DNS Infrastruktur durchgeführt wurde. Es soll nicht einzelne kompromittierte DNS Server oder DNS Caches auffinden. Daher wird nur ein einzelner Server von einer Location aus abgefragt.
### /K27/
Eine Ausweitung auf mehrere DNS Server kann in einem Folgeprojekt realisiert werden. 
### /K30/
Das Datenbank System besitzt eine Schnittstelle die von DH über das LAN des if(is) genutzt werden kann.
### /K40/
Der Mailserver, welchen DH ggf. benutzen kann, besitzt eine Schnittstelle die DH über das LAN der if(is) ansprechen kan

![Abb.: 1 Kontextdiagramm](Dokumentation/WIP/Kontextdiagramm.png)



## 2.4    Funktionale Anforderungen
## /F1XX/ Allgemeine Anforderungen
### /F110/
Der User muss eine (Sub)Domain zur Überwachung hinzufügen und entfernen können.
### /F120/
Zu eineer (Sub)Domain soll der User empfehlungen für vorhandene Subdomains erhalten. Diese werden über ein Wörterbuch gesucht und überprüft ob DNS Informationen vorliegen. Nur vorhandene Subdomains werden vorgeschlagen.
### /F130/
Es soll dem User möglich sein eine größere Menge an (Sub)Domains als Batch Import hinzuzufügen.


## /F2XX/ Frontend
### /F210/
Der User soll unterschiedliche Formen von Berichten anfordern können. Die Berichte sollen nach unterschiedlichen Kriterien gefiltert werden können. Die Kriterien sind: Zeitraum des Vorfalls, Betroffene (Sub)Domain, DH- Scoring
### /F210/
Der User soll Domainvorfälle kommentieren und kategorisieren können.

## /F3xx/ Datenerhebung
### /F310/
DH muss zu jeder Domain die zu beobachten ist regelmäßig zyklisch Daten vom öffentlichen DNS System erfragen.
### /F312/
Es sind folgende DNS Resource Record aufzulösen:
- A
- AAAA
- NS
- MX
- TXT
### /F314/
Zu den Jeweiligen DNS Resource Record /F312/ sind auch die TTL und beim MX Record auch die Priorität aufzulösen. 
### /F320/
Zusätzlich zu den reinen DNS Informationen werden zu den aufgeösten IP Adressen (A/AAAA-Records) auch Informationen über das WHOIS System abgefragt.
### /F322/
Bei /F320/ sollen Folgende Daten zu einer IP Adresse erhobenen werden:
- CIDR/Subnetz
- Person/Organisation
- Country
- Phone
### /F330/
Weitere Daten Quellen ggf. sind noch TBD
### /F340/
Das Abfrage Intervall ist 1/Tag und kann ggf. anhängig von den zur Verfügung stehenden Ressourcen gesteigert werden
### /F350/
Die Datenerhebung erfolgt automatisch und muss nicht manuell angestoßen werden. 

## /F4XX/ Datenbank System
### /F410/
Alle Domain Abfragen sollen persistent in einer Datenbank gespeichert werden.
### /F420/
Welche Daten genau gespeichert werden ist TBD.
## /F5XX/ Backend
### /F510/
Ein Rechtesystem wird nicht eingeführt. Nur ein User wird implementiert. Damit haben alle Benutzer die gleichen Rechte und vollen Zugriff
 
## /F6XX/ Scoring System 
### /F610/
Zu jeder Domain Veränderung muss automatisch ein DH-Scoring erstellt werden. Das DH- Scoring soll dem User einen Anhaltspunkt geben wie wahrscheinlich es ist das es sich bei einer Domain Veränderung um eine unberechtigte Veränderung gehalten hat. 
### /F620/
Das DH-Scoring verwendet eine Scala von 0 (Missbrauch sehr unwahrscheinlich) bis 10 (Missbrauch sehr wahrscheinlich).

## 2.5    Qualitätsanforderungen
### /Q10/
Domainabfragen können unverschlüsselt erfolgen.
### /Q11/
Der Zugriff auf DH muss verschlüsselt erfolgen
### /Q20/
Die erhobenen Daten können unverschlüsselt in der Datenbank gespeichert werden. 
### /Q30/
Der Programmcode ist so zu kommentieren, dass die Funktionen des Codes von einer Fachkundigen Person verstanden werden kann.
### /Q31/
Die Kommentate werden in Deutsch erstellt.  

## 2.6    Abnahmekriterien
### /A10/
Das DH erfasst von mindestens 500 Domains über mindestens zwei Wochen Domainveränderungen und hält diese fest.
### /A20/
Wird DH mit historischen echten oder fiktiven  Daten einer Domain Übernahme versorgt. Der Scoringwert muss hier über 5 liegen.
### /A30/
Zum DH wird ein Benutzer-Handbuch erstellt. 
