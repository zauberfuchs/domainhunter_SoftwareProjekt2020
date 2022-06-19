import time
import dns.resolver
from datetime import datetime
from datetime import timedelta
from connection import Connection
from domain import Domain
import psycopg2
from scorer import Scorer
from logger import logger_scheduler


class Scheduler():

    def __init__(self):
        # updateTime (in Minuten).speichert wie haeufig eine  Domain aktuallisiert werden soll
        self.update_time = 1440
        # waitTime (in Minuten) speichert wie lange nach leeren von nextFQDNs gewartet werden soll
        # um nach neuen zu aktuallisirenden Domains zu suchen.
        self.wait_time = 5
        # dbConnection hält die Datenbank Connection für den scheduler
        self.db_connection = Connection()
        logger_scheduler.info(f'scheduler: setting up new scheduler with parameters: '
                              f'waitTime: {self.wait_time} minutes, updateTime: {self.update_time} minutes')

    # running speichert den Status des schedulers und dient als Abbruchkriterium.
    running = False
    # nextFQDNs speichert als Liste die FQDNs bei welchen ein Update durchgeführt werden soll.
    nextFQDNs = []

    # Methode zum Starten des schedulers, er läuft solange in der Endlosschleife bis er gestopt wird.
    def start(self):
        self.running = True
        self.db_connection.connect()

        while (self.running):
            # print("Dies ist der " + str(runs)+ " Durchlauf")
            self.nextFQDNs = self.get_next_domains()
            worked_on_fqd_ns = 0
            for fqdn in self.nextFQDNs:
                logger_scheduler.info('scheduler: currently working on: ' + fqdn)
                try:
                    Domain(fqdn, False, self.db_connection, logger_scheduler).update_db_record()
                    worked_on_fqd_ns += 1
                except dns.resolver.Timeout as error:
                    logger_scheduler.error(f'Scheduler.start:dnsquery: dns.resolver.Timeout:  {error}')
                    pass
                except dns.resolver.NoNameservers as error:
                    logger_scheduler.error(f'Scheduler.start:dnsquery: dns.resolver.NoNameservers:  {error}')
                    pass
                except psycopg2.DatabaseError as error:
                    logger_scheduler.error(f'Scheduler.start:database error occurred: {error}')

            self.nextFQDNs = []

            scorer = Scorer(self.db_connection)

            scorer.start()

            # sollte im letzten durchlauf keine Domain bearbeitet worden sein wartet der scheduler
            if worked_on_fqd_ns == 0:
                logger_scheduler.info(f'scheduler: scheduler is waiting: {self.wait_time} minutes')
                time.sleep(self.wait_time * 60)

    # Mit dieser Methode soll die Endlosschleife beendet werden.
    def stop(self):
        self.running = False
        self.db_connection.disconnect()
        logger_scheduler.info('scheduler.stop: scheduler was stopped properly due to stop function')

    def get_next_domains(self):
        next_fqdns = []
        if not self.db_connection.connected:
            self.db_connection.connect()
            logger_scheduler.info('scheduler.get_next_domains: successfully established database connection')
        conn = self.db_connection.conn

        now = datetime.now()
        # Das Datum inkl Uhrzeit vor welchem die last_change wert der Domain liegen muss wird berechnet
        from_datetime = now - timedelta(minutes=int(self.update_time))
        # Und zu einem String konvertiert.
        from_datetime_as_string = str(from_datetime.strftime("%Y/%m/%d %H:%M:%S"))

        try:
            # Cursor wird erstellt
            cur = conn.cursor()
            # Select von allen Domains die nach dem fromeDatetime liegen.
            postgres_select_query = "SELECT fqdn FROM domain WHERE last_change < \'" + from_datetime_as_string + "\';"

            cur.execute(postgres_select_query)

            # TO_Do: performatere variante finden
            i = 0
            while i < cur.rowcount:
                next_fqdns.append(cur.fetchone()[0])
                i += 1

            # Cursor schließen
            cur.close()
            logger_scheduler.info(
                f'scheduler.get_next_domains: successfully extracted  {len(next_fqdns)} domains from the database')

        except (psycopg2.DatabaseError) as error:
            logger_scheduler.error(f'scheduler.get_next_domains: database error occurred: {error}')
        except (Exception,) as error:
            logger_scheduler.error(f'scheduler.get_next_domains: Error occurred: {error}')
        return next_fqdns
