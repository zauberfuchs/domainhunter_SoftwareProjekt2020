from datetime import datetime
import time
from connection import Connection
from domainquery import Domainquery
from logger import logger_cli
from logger import logger_scheduler


class Domain():

    # erstellt ein Domain Objekt mit abfrage ob es sich um eine
    # neue Domain handelt oder eine die es schon in der Datenbank gibt
    def __init__(self, fqdn, new, db_connection, logger):
        self.new = new
        if(self.new):
            self.added_date = str(datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
            self.second_level_domain = fqdn.split('.')[-2]
        self.fqdn = fqdn
        self.last_change = str(datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
        self.top_level_domain = fqdn.split('.')[-1]
        self.execute_domainquery(fqdn)
        self.connection = db_connection
        self.logger = logger

    # updated die Datenbanktabelle "Domain" und erstellt dannach eine neue Domainquery mit den dazugehörigen Records
    def update_db_record(self):
        # erstelle cursor
        cur = self.connection.conn.cursor()
        # domain updaten
        postgres_update_query = 'UPDATE domain SET last_change = ''\''+ self.last_change + '\'' + 'WHERE fqdn = \'' + self.fqdn + '\';'

        cur.execute(postgres_update_query)

        # erstelle neuen Tabellen eintrag in domain_query
        postgres_insert_domainquery = 'INSERT INTO domain_query (fqdn, query_time, scoring_value, comment, category) VALUES(''\'' + self.fqdn + '\',' \
                                                            '\'' + self.new_domain_query.query_time + '\',' \
                                                            '\'' + '-1' + '\',' \
                                                            '\'' + '' + '\',' \
                                                            '\'' + self.new_domain_query.category + '\');'
        cur.execute(postgres_insert_domainquery)
        self.logger.info("domain.update_db_record: updated db record of " + self.fqdn)

##################################################################################################################
###                                               Records speichern                                            ### 
##################################################################################################################

    # speichere falls vorhanden die records zu der domainquery in die datenbank
        if(self.new_domain_query.a_records is not None):
            for aRecord in self.new_domain_query.a_records:
                postgres_insert_record= 'INSERT INTO a_record (ipv4_address, ttl, fqdn, query_time) VALUES(''\'' + str(aRecord.ipV4) + '\',' \
                                                                '\'' + str(aRecord.ttl) + '\',' \
                                                                '\'' + str(self.fqdn) + '\',' \
                                                                '\'' + str(self.new_domain_query.query_time) + '\');'
                cur.execute(postgres_insert_record)
                postgres_insert_record= 'INSERT INTO ipv4_whois_query  (query_time, ipv4_address, phone, person, organisation, cidr_subnet, country, raw_data, fqdn) VALUES(''\'' + str(self.new_domain_query.query_time) + '\',' \
                                                                '\'' + str(aRecord.ipV4) + '\',' \
                                                                '\'' + str(aRecord.whoIsQuery.phone) + '\',' \
                                                                '\'' + str(aRecord.whoIsQuery.person) + '\',' \
                                                                '\'' + str(aRecord.whoIsQuery.organisation) + '\',' \
                                                                '\'' + str(aRecord.whoIsQuery.cidr) + '\',' \
                                                                '\'' + str(aRecord.whoIsQuery.country) + '\',' \
                                                                '\'' + str(aRecord.whoIsQuery.raw) + '\',' \
                                                                '\'' + str(self.new_domain_query.fqdn) + '\');'
                cur.execute(postgres_insert_record)
            del(self.new_domain_query.a_records)

        if(self.new_domain_query.aaaa_records is not None):
            for aaaaRecord in self.new_domain_query.aaaa_records:
                postgres_insert_record= 'INSERT INTO aaaa_record (ipv6_address, ttl, fqdn, query_time) VALUES(''\'' + aaaaRecord.ipV6 + '\',' \
                                                                '\'' + str(aaaaRecord.ttl) + '\',' \
                                                                '\'' + str(self.fqdn) + '\',' \
                                                                '\'' + str(self.new_domain_query.query_time) + '\');'
                cur.execute(postgres_insert_record)
                postgres_insert_record= 'INSERT INTO ipv6_whois_query  (query_time, ipv6_address, phone, person, organisation, cidr_subnet, country, raw_data, fqdn) VALUES(''\'' + str(self.new_domain_query.query_time) + '\',' \
                                                                '\'' + str(aaaaRecord.ipV6) + '\',' \
                                                                '\'' + str(aaaaRecord.whoIsQuery.phone) + '\',' \
                                                                '\'' + str(aaaaRecord.whoIsQuery.person) + '\',' \
                                                                '\'' + str(aaaaRecord.whoIsQuery.organisation) + '\',' \
                                                                '\'' + str(aaaaRecord.whoIsQuery.cidr) + '\',' \
                                                                '\'' + str(aaaaRecord.whoIsQuery.country) + '\',' \
                                                                '\'' + str(aaaaRecord.whoIsQuery.raw) + '\',' \
                                                                '\'' + str(self.fqdn) + '\');'

                cur.execute(postgres_insert_record)
            del(self.new_domain_query.aaaa_records)

        if(self.new_domain_query.ns_records is not None):
            for nsRecord in self.new_domain_query.ns_records:
                postgres_insert_record= 'INSERT INTO ns_record (ns, ttl, fqdn, query_time) VALUES(''\'' + str(nsRecord.nsDomain) + '\',' \
                                                                '\'' + str(nsRecord.ttl) + '\',' \
                                                                '\'' + str(self.fqdn) + '\',' \
                                                                '\'' + str(self.new_domain_query.query_time) + '\');'
                cur.execute(postgres_insert_record)
            del(self.new_domain_query.ns_records)

        if(self.new_domain_query.mx_records is not None):
            for mxRecord in self.new_domain_query.mx_records:
                postgres_insert_record= 'INSERT INTO mx_record (preference, host_name, ttl, fqdn, query_time) VALUES(''\'' + str(mxRecord.preference) + '\',' \
                                                                '\'' + str(mxRecord.host_name) + '\',' \
                                                                '\'' + str(mxRecord.ttl) + '\',' \
                                                                '\'' + str(self.fqdn) + '\',' \
                                                                '\'' + str(self.new_domain_query.query_time) + '\');'
                cur.execute(postgres_insert_record)
            del(self.new_domain_query.mx_records)

        if(self.new_domain_query.text_records is not None):
            for textRecord in self.new_domain_query.text_records:
                postgres_insert_record= 'INSERT INTO text_record (text, ttl, fqdn, query_time) VALUES(''\'' + str(textRecord.txt) + '\',' \
                                                                    '\'' + str(textRecord.ttl) + '\',' \
                                                                    '\'' + str(self.fqdn) + '\',' \
                                                                    '\'' + str(self.new_domain_query.query_time) + '\');'
                cur.execute(postgres_insert_record)
            del(self.new_domain_query.text_records)
       
        #a enderung durchfuehren
        self.connection.conn.commit()
        # Datenbank Verbindung mit der PostgreSQL schließen
        cur.close()
        

    def write_db_record(self):
        # create a cursor
        cur = self.connection.conn.cursor()
        #SQL_Befehl eingeben
        postgres_insert_query = 'INSERT INTO domain (fqdn, added_date, last_change, top_level_domain, second_level_domain) VALUES(''\'' + self.fqdn + '\',' \
                                                            '\'' + self.added_date + '\',' \
                                                            '\'' + self.last_change + '\',' \
                                                            '\'' + self.top_level_domain + '\',' \
                                                            '\'' + self.second_level_domain + '\');'
        cur.execute(postgres_insert_query)
        # aenderung durchfuehren
        self.connection.conn.commit()
        # Datenbank Verbindung mit der PostgreSQL schließen
        cur.close()
        
    # erstelle ein Domainquery Objekt
    def execute_domainquery(self, fqdn):
        self.new_domain_query = Domainquery(fqdn)
        self.new_domain_query.add_category('1')
