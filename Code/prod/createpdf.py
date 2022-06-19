from fpdf import FPDF 
import os 
from datetime import datetime 
import psycopg2 
from config import config


#PDF Klasse
class PDF(FPDF):
    #def __init__(self):
        



    #Kopfzeile mit Logo und Titel
    def header(self): 
        self.image('logo1.png',10,2,80)
        # Arial bold 15
        self.set_font('Arial', 'I', 10)
        #Title unter dem Logo Zeitpunkt für den Report Zeit
        date_time = datetime.now().strftime("%d-%m-%Y-%H:%M:%S") 
        text = 'Report ' + date_time 
        self.text(12,18,text)
        #Line zum abgrenzen
        self.line(0,20, 220, 20);
        #Line break
        self.ln(20)

    #Fusszeile mit Seitenanzahl
    def footer(self):
        #Position 1.5 cm von unten
        self.set_y(-15)
        #Arial italic 8
        self.set_font('Arial', 'I', 8)
        #Seiten Anzahl
        self.cell(0, 10, 'Page ' + str(self.page_no()) + '/{nb}', 0, 0, 'R')

    #Report erstellen und als pdf ausgeben
    def bigreport(self,data): 
        now = datetime.now() 
        date_time = now.strftime("%d-%m-%Y")
        self.alias_nb_pages() 
        self.add_page() 
        self.set_font('Arial','I',10)
        #column width auf 1/4 der Seiten groese
        epw = self.w - 2*self.l_margin 
        col_width = epw/4
        #Setzen des Tabellen Ueberschrift
        self.set_font('Arial','B',12.0) 
        self.cell(epw, 0.0, 'Your choice of Domain Queries', align='L') 
        self.set_font('Arial','B',10.0) 
        self.ln(3)
        #Die height des aktuellen Fonts bekommen
        th = self.font_size + 0.1
        #List durchgehen und den jeweiligen Inhalt in eine Cell schreiben
        for idx, row in enumerate(data):
            #Nur die erste Zeile Fett gedruckt schreiben
            if idx > 0: self.set_font('Arial', '',10.0)
            
            for idx, datum in enumerate(row):
                #Die jeweilige width setzen
                if idx == 1: 
                    self.cell(35,th,str(datum), border=1) 
                elif idx == 2: 
                    self.cell(26,th,str(datum), border=1) 
                elif idx == 4: 
                    self.cell(16,th,str(datum), border=1) 
                elif idx == 5: 
                    self.cell(41,th,str(datum), border=1) 
                else:
                    self.cell(40,th,str(datum), border=1)
            #Naechste Zeile
            self.ln(th)
        #Dateiname definieren
        ausgabe = 'Report' + date_time + '.pdf'
        #pdf ausgabe Ort
        self.output('./Reports/'+ausgabe,'F')
        #pdf beenden
        self.close()
