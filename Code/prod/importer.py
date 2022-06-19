import csv
from domain import Domain
from subdomain import find_subdomains_dns
import psycopg2
import scheduler
import re
from logger import logger_cli


class Importer:
    
    # erstellt einen Importer und bekommt eine Datenbank Connection übergeben
    def __init__(self, db_connection):
        self.connection = db_connection
        self.count_imported_domains = 0
        self.count_skipped_domains=0
        self.subdomains = open("subdomains-1000.txt").read().splitlines()
    
    # Methode um die Bruteforce Datei zu ändern
    def change_subdomain_file(self, subdomain_number):
        if(subdomain_number == 100):
            self.subdomains = open("subdomains-100.txt").read().splitlines()
        elif(subdomain_number == 1000):
            self.subdomains = open("subdomains-1000.txt").read().splitlines()
        else:
            self.subdomains = open("subdomains-10000.txt").read().splitlines()

    def import_from_csv(self, path, find_subdomain = False):
        """Importiert Domains von einer CSV Datei.
        Der 1.Paramter ist der vollstaendigen Pfad der CSV Datei.
        Der 2.Paramter ist das uebergebene dbConnection Objekt.
        Der 3.Paramter gibt an, ob nach Subdomains gesucht werden soll.
        (Standartmaeßig wird nicht nach Subdomains gesucht)
        """
        number_added_domains = 0  # Anzahl hinzugefuegte Domains

        # alle in der Datenbank vorhandenen Domains werden abgefragt
        added_fqdns=[]

        try:
            with open(path) as csvdatei:
                csv_reader_object = csv.reader(csvdatei)

                for row in csv_reader_object:
                    if row :
                        fqdn = row[0]
                        fqdn_tuple = (str(fqdn),)
                        if fqdn in added_fqdns:
                            print(f'The FQDN: {fqdn} is present multiple times in the CSV file and only added ones.')
                            self.count_skipped_domains += 1
                            # Prüfung ob es sich um eine gültige schreibweise für eine Domain handelt.
                        elif not re.match('^((?!-)[A-Za-z0-9-]{1,63}(?<!-)\\.)+[A-Za-z]{2,6}$',fqdn):
                            print(f'{fqdn} ist not a valid Domain.')
                        else:
                            self.create_domain(fqdn, find_subdomain)
                            added_fqdns.append(fqdn)

        except FileNotFoundError as error:
            print(str(error))
            print('enter filename and path to be imported, append " -sd" to check for subdomains\n'
                  '[syntax: /home/user/file.csv -sd]')
        except Exception as error:
            logger_cli.error(f'Importer.import_from_csv: {error}')
            print('An Error occurred during the Import, please check logfile for details')



        message_number_added_domains = f'\n Successfully added {self.count_imported_domains} Domains.\n '
        print(message_number_added_domains)
        if self.count_skipped_domains > 1 :
            message_skipped_fqdns = f'\n While the Import {self.count_skipped_domains} FQDNs were skiped.\n'
            print(message_skipped_fqdns)

    def create_domain(self, fqdn, find_subdomain):
        """ Erzeugt ein Domain-Objekt aus einem String und fuehrt auf diese
        write_db_record und update_db_record aus.
        Falls findSubDomain = True werden alle Subdomains ins DB geschrieben.
        Danach wird das nicht mehr benoetigte Objekt geloescht.
        """
        all_domains = self.get_all_domains()
        #Prüfung ob der FQDNs bereits in der Datenbank vorhanden ist.
        if not self.validate_if_domains_in_db(fqdn, all_domains):
            domain_object = Domain(fqdn, True, self.connection, logger_cli)
            domain_object.write_db_record()
            self.count_imported_domains += 1
            domain_object.update_db_record()
            print(f'Domain {fqdn} successfully imported')

            if(find_subdomain):
                self.create_subdomains(fqdn)
    
    # prüft ob eine Domain bereits in der Datenbank existiert
    def validate_if_domains_in_db(self, fqdn, fqdns_in_db):
        is_present = False
        if any(fqdn in s for s in fqdns_in_db):
            print(f'The Domain with FQDN: {fqdn} is already present in the Database.')
            self.count_skipped_domains += 1
            is_present = True
        return is_present

    # erstellt die subdomains zu einem fqdn
    def create_subdomains(self, fqdn):
        subdomainliste = find_subdomains_dns(fqdn, 2, self.subdomains)
        all_domains = self.get_all_domains()
        for subdomain in subdomainliste:
            if not self.validate_if_domains_in_db(subdomain, all_domains):
                domain_object = Domain(subdomain, True, self.connection, logger_cli)
                self.count_imported_domains += 1
                domain_object.write_db_record()
                domain_object.update_db_record()
                
    # holt sich alle domains aus der Datenbank
    def get_all_domains(self):
        all_domains = []

        if not self.connection.connected:
            self.connection.connect()
            logger_cli.info('Importer.get_all_domains: successfully established database connection')
        conn = self.connection.conn

        try:
            # Cursor wird erstellt
            cur = conn.cursor()
            # Select von alle Domains.
            postgres_select_query = 'select fqdn from domain; '

            cur.execute(postgres_select_query)

            all_domains = cur.fetchall()

            # Cursor schließen
            cur.close()
            logger_cli.info(f'Importer.get_all_domains: successfully extracted {len(all_domains)}  Domains')
        except psycopg2.DatabaseError as error:
            logger_cli.error(f'Importer.get_all_domains: database error occurred: {error}')
        except Exception as error:
            logger_cli.error(f'Importer.get_all_domains: Error occurred: {error}')
        return all_domains
