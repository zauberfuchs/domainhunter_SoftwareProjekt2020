from datetime import datetime

import dnsquery


class Domainquery:

    # Konstruktor mit fqdn. Die Methode execute_dns_query wird ausgeführt um die Records mit daten zu füllen.
    def __init__(self, fqdn):
        self.fqdn = fqdn  # Hier wird der FQDN der gespeichert zu welchem der Doaminquery gehoert.
        self.ns_records = []  # Eine Liste mit allen NS-Records des Domainquerys
        self.a_records = []  # Eine Liste mit allen A-Records des Domainquerys
        self.mx_records = []  # Eine Liste mit allen MX-Records des Domainquerys
        self.aaaa_records = []  # Eine Liste mit allen AAAA-Records des Domainquerys
        self.text_records = []  # Eine Liste mit allen text-Records des Domainquerys
        self.execute_dns_query()  # Damit der query auch direkt mit records gefüllt ist wird die DNS abfrage erstellt.
        # Hier wird der Zeitpunkt des Querys gespeichert.
        self.query_time = str(datetime.now().strftime("%Y/%m/%d %H:%M:%S"))

    def add_score(self, score):
        # Der Score soll Auskunft darüber geben ob auffaelliger Veraenderungen vorliegen.
        # Der Wert soll zwischen 0-10 liegen.
        self.score = score

    def add_comment(self, comment):
        self.comment = comment  # Hier können Kommentare zu dem Domainquery gespeichert werden

    def add_category(self, category):
        self.category = category  # Hier wird die Kategorie des Querys gespeichert.

    # Mit dieser Methode sollen die Records dieses Querrys mit den Daten aus der DNS abfrage gefüllt werden.
    def execute_dns_query(self):
        
        dns_results = dnsquery.get_records(self.fqdn)

        self.a_records = dns_results['A']
        self.aaaa_records = dns_results['AAAA']
        self.ns_records = dns_results['NS']
        self.mx_records = dns_results['MX']
        self.text_records = dns_results['TXT']
        self.query_time = str(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
