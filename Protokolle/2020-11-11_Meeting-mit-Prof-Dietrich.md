# 2020-11-11 Wöchentliches Meeting
- Uhrzeit ca: 14:00-17:00
# Anwesend:
 - Julien Förderer
 - Nico Hegemann
 - Ibrahim Cevik
 - Michael Kalamarski
 - Arne Thiel 
    #### Ab 16:00:
 - Prof. Dietrich
 - S. Michalik 
 - Raphale Springer


# Tätigkeiten:
- ### Besprechung Fortschritt / aktueller Stand
    * Michael: Hatte Probleme beim Erstellen der Datenbank
    * Nico: WhoIs query ergänzt um die "Funktion" von Mehreren Server die Daten zu erfragen 
    * Ibrahim: Hat noch eine digany Test methode erstellt. Läd später noch hoch. 
    * Julien: Hat einer fertige Digany mehthode erstellt und updatet diese noch. 
    * Arne: Hat das Grundgerüst für die Domainyquerry erstellt. 


# Besprechung mit Prof. Dietrich:
- ### Fragen
    * Wie bekommt man Objekte zurück aus der DB
        * Daten erfragen und dann in einen Konstruktor
    * Arbeiten auf dem MasterBranch?
        * Arbeiten auf der Master Branch wird geduldet. 
    * Show and Tell /Abgabedatum
        * keine aktuelleren Infos

- ### Anregungen von Prof. Dietrich 
    * Wie verhält sich der Scheduler wenn er richtig viel zu tun hat. (Ansatz Idee z.B. wenn der Scheduler Domains aus der DB holt direkt mehrere hohlen um)
    * ggf. schon vom scheduler den previous domainquerry mitgeben
    * vll. noch einen dedizierten scorer erstellen 

 - ### Absprachen mit Prof. Dietrich
    * nächstes Treffen 25.11.2020





# to Do 18.11.:

- ### Michale:
    * DB Grundgerüst auf Server bis 12.11. "final" bis zum 18.11. 
- ### Julien:
    * richtet Git auf dem Server ein und beginnt mit der Klasse Domain, insbesondere mit der Methode findeSubdomain.  
- ### Nico:
     * Unterstütz Micheal DB und macht sich Gedanken über die Menu Struktur
- ### Arne:
    * Erweitert Domainquery um Digany und arbeitet am Scorring algo
- ### Ibrahim: 
    * erstellt den Importer. 
