import csv
import os.path
from datetime import datetime

#Klasse zur Erstellung einer Csv Datei
class CsvOut():

 #initialisierung
 def __init__(self,data): 
     self.data = data

 #Methode export_csv
 def export_csv(self):
     now = datetime.now()
     #date_time = now.strftime("%m-%d-%Y-%H-%M-%S")
     #Aktuelles Datum als Dateiname definieren
     date_time = now.strftime("%d-%m-%Y")
     namecsv = 'Report' + date_time + '.csv'
     #w ist write wipes existing file
     #r ist read
     #a append mode write to end of file !Achtung Name muss statisch sein
     with open('./Reports/'+ namecsv, 'w') as csvfile: 
        writer = csv.writer(csvfile, delimiter=',')
        #Schreibt jede Row in die csv getrennt durch ,
        writer.writerows(self.data)
        


