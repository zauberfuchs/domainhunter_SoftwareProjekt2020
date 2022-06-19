from datetime import datetime
import psycopg2
from connection import Connection
from logger import logger_scheduler


class Scorer:

    def __init__(self, db_connection=Connection()):
        self.db_connection = db_connection

    # Mit start wird der Scorere gestartet.
    # Er berechnet für alle noch nicht gescorten Domainquerrys den Score und trägt diesen in die DB ein.
    def start(self):
        completed = False
        retries = 0
        while not completed:
            try:

                for unscored_domainquery in self.get_unscored_domainqueries():
                    previous_domainquerry = \
                        self.get_previous_domainquerry(unscored_domainquery[1], unscored_domainquery[0])
                    if previous_domainquerry is not None:
                        score_result = self.calculate_score(unscored_domainquery, previous_domainquerry)
                        score = score_result[0]
                        score_type = score_result[1]
                    else:
                        score = 0
                        score_type = 'No_Score'

                    self.write_score(unscored_domainquery[1], unscored_domainquery[0], score, score_type)
                completed = True

            except (Exception, psycopg2.DatabaseError) as error:
                logger_scheduler.error(f'Scorer.start: database error occurred: {error}')
                # da die Datenbank leider immer wieder Aussetzer hat,
                # wird bei einem Datenbank Fehler der Vorgang nochmal angestossen
                retries = retries + 1
                if retries < 99:
                    self.db_connection.connect()
                    logger_scheduler.info('successfully established database connection')
                    continue

                else:
                    completed = True
                    logger_scheduler.error(f'Scorer.start: Failed after {retries} retries')

    # recalculate kann genutzt werden um nach einer Umstellung des Algorithmuses alle Domanquerrys neu zu berechnen.
    def recalculate(self, fqdn='any', print_progress=False):

        try:
            rescore_domainquerys = self.get_all_domainqueries()
            if fqdn == 'any':
                total_number = len(rescore_domainquerys)
            else:
                # toDo: Nice to have man könnte hier noch den Zahlenwert anpassen wenn man nur nach einer FQDN sucht.
                total_number = len(rescore_domainquerys)
            progress_number = 0

        except psycopg2.DatabaseError as error:
            logger_scheduler.error(f'Scorer.recalculate: database error occurred: {error}')
            # da die Datenbank leider immer wieder Aussetzer hat,
            # wird bei einem Datenbank Fehler der Vorgang nochmal angestossen
            self.recalculate()
        except Exception as error:
            logger_scheduler.error(f'Scorer.recalculate: Error occurred: {error}')

        for rescore_domainquery in rescore_domainquerys:
            try:
                if fqdn == 'any':
                    previous_domainquerry = \
                        self.get_previous_domainquerry(rescore_domainquery[1], rescore_domainquery[0])
                    if previous_domainquerry is not None:
                        score_result = self.calculate_score(rescore_domainquery, previous_domainquerry)
                        score = score_result[0]
                        score_type = score_result[1]

                    else:
                        score = 0
                        score_type = 'No_Score'

                    progress_number += 1
                    if print_progress and progress_number % 5 == 0:
                        print(f'Rescored: {rescore_domainquery[1]} Score: {score}  Score Reason: {score_type}'
                              f' number: {progress_number}/{total_number}')
                    self.write_score(rescore_domainquery[1], rescore_domainquery[0], score, score_type)

                if fqdn != 'any':

                    if rescore_domainquery[1] == fqdn:
                        previous_domainquerry = \
                            self.get_previous_domainquerry(rescore_domainquery[1], rescore_domainquery[0])
                        if previous_domainquerry is not None:
                            score_result = self.calculate_score(rescore_domainquery, previous_domainquerry)
                            score = score_result[0]
                            score_type = score_result[1]
                        else:
                            score = 0
                            score_type = 'No_Score'

                        progress_number += 1
                        if print_progress:
                            print(f'Rescored: {rescore_domainquery[1]} Score: {score}  Score Reason: {score_type}'
                                  f' number: {progress_number}/{total_number}')
                        self.write_score(rescore_domainquery[1], rescore_domainquery[0], score, score_type)

            except psycopg2.DatabaseError as error:
                logger_scheduler.error(f'Scorer.recalculate: database error occurred: {error}')
                rescore_domainquerys.append(rescore_domainquery)
            except Exception as error:
                logger_scheduler.error(f'Scorer.recalculate: Error occurred: {error}')

        self.db_connection.disconnect()

    # calculate_score berechnet den score Wert zwischen zwei übergebenen Domainquerrys.
    # Es wird der höchste Score zurückgegeben und
    # ein String in dem alle Recordtypen aufgelistet sind die einen Score > 1 ausgelöst haben.
    def calculate_score(self, unscored_domainquery, previous_domainquerry):
        score = 0
        scored_type = 'No_Score'
        types = ['NS', 'MX', 'IPV4', 'IPV6', 'TEXT']

        for type in types:

            # Variable zum übergeben ob alle WHOis einträge Null sind die Abfrage also scheiterte (Blocked by RIPE)
            whois_null = False

            unscored_records = self.get_record(type, unscored_domainquery[1], unscored_domainquery[0])
            previous_records = self.get_record(type, previous_domainquerry[1], previous_domainquerry[0])
            type_score = 0
            # wenn es bis jetzt keinen Eintrag zu diesem Typ von Record gab wird erst mal ein Score von 4 vergeben.
            if previous_records is None:
                type_score = 4

            elif unscored_records != previous_records:

                # die neuen Records (unscored_records) werden mit den vorherigen (previous_records) verglichen
                # und die Einträge unterteilt:

                # new_records sind records die vorher so nicht vorhandne waren.
                new_records = []
                # removed_records waren in denn previous_records vorhanden und wurden entfernt
                removed_records = []
                # changed_records sind records bei denen sich lediglich ein einzelner Wert (z.b. ttl) verändert hat.
                changed_records = []

                # Es wird über die Liste der unscored_records itteriert die records liegen als Tupel vor:
                for record in unscored_records:
                    # daher wird zuerst gepüft ob das Tupel identisch auch in den previous_records vorhanden ist
                    if record not in previous_records:
                        # falls nicht wird überprüft ob ein Tupel mit dem gleichen Hauptmerkmal (IP, Hostname) vorliegt,
                        # daher nur ein Parameter verändert wurde.
                        hit = False
                        for previous_record in previous_records:

                            if record[0] == previous_record[0]:
                                changed_records.append(record)
                                hit = True
                        if not hit:
                            new_records.append(record)
                # Um auch gelöschte Records zu finden wird das Vorgehen von Oben
                # analog für aus Sicht der previous_records durchgeführt.
                for previous_record in previous_records:
                    if previous_record not in unscored_records:
                        hit = False
                        for record in unscored_records:
                            if record[0] == previous_record[0]:
                                hit = True
                        if not hit:
                            removed_records.append(previous_record)

                changed_score = 0
                remove_score = 0
                new_score = 0

                if type == 'NS' or type == 'MX':
                    if type == 'NS':
                        basis_score = 7
                    else:
                        basis_score = 5

                    if changed_records:
                        changed_score = 0.3
                    if removed_records:
                        remove_score = 0.4

                    if new_records:
                        new_score = 0
                        for new_record in new_records:
                            second_level_domain = unscored_domainquery[1].split('.')[-2] + '.' \
                                                  + unscored_domainquery[1].split('.')[-1]
                            # Case 1: Der neue NS Host Name liegt in der second_level_domain
                            # (zb.: NS1.w-hs.de-> NS2.w-hs.de)
                            if (second_level_domain in str(new_record[0])):
                                new_score = max(0.3, new_score)

                            if (second_level_domain not in str(new_record[0])):
                                for previous_record in previous_records:
                                    hit = False

                                    second_level_domain_previous_record = previous_record[0].split('.')[-2] + '.' + \
                                                                          previous_record[0].split('.')[-1]
                                    # Case 2: Der neue NS Host Name liegt in der gelichen second_level_domain wie in der
                                    # vorherigen Querry  (zb.: dns-1.dfn.de.-> dns-2.dfn.de für die Domain w-hs.de)
                                    if second_level_domain_previous_record in str(new_record[0]):
                                        hit = True
                                        new_score = max(0.7, new_score)
                                    # Case 3 kein Zusammenhang zu bekannten daten.
                                    if not hit:
                                        new_score = max(1.2, new_score)

                    # der maximale score wird bestimmt und als indication_value eingesetzt.
                    indication_value = max(changed_score, remove_score, new_score)
                    type_score = indication_value * basis_score

                elif type == 'IPV4' or type == 'IPV6':
                    basis_score = 2

                    # IP ist identisch aber TTL hat sich verändert. Daher nicht soo interesannt:
                    if changed_records:
                        changed_score = 0.51
                    # Ein Record wurde entfernt.
                    if removed_records:
                        remove_score = 1.2
                    # Ein Neuer Eintrag wurde hinzugefügt.
                    if new_records:
                        new_score = 1
                        # für alle Neuen Records wird ein....
                        for new_record in new_records:

                            case_1 = False
                            case_2 = False
                            case_3 = False
                            case_4 = False
                            # ....Vergleich mit den  alten Records durchgeführt.
                            for previous_record in previous_records:

                                # Case 1: IP "Besizer" identisch/abweichend (2 von 3 Werten reichen)
                                if (new_record[1] == previous_record[1] * 1 +
                                    new_record[2] == previous_record[2] * 1 +
                                    new_record[3] == previous_record[3] * 1) >= 2: case_1 = True

                                # Case 2: IP Subnetz identisch/abweichend
                                if new_record[4] == previous_record[4]:
                                    case_2 = True
                                # Case 3: IP Country identisch/abweichend
                                if new_record[5] == previous_record[5]:
                                    case_3 = True
                                # Case 4: Für beide IPs keine whois informationen (ggf. Ripe gesperrt)
                                if (new_record[1] == previous_record[1] == 'null' and
                                        new_record[2] == previous_record[2] == 'null' and
                                        new_record[3] == previous_record[3] == 'null' and
                                        new_record[4] == previous_record[4] == 'null' and
                                        new_record[5] == previous_record[5] == 'null'):
                                    case_4 = True

                        # Ergebnis dieses einen record wird brechnet:
                        # Fall 1 (0,3/2) * Fall 2 (0,5/3) * Fall 3 (0,5/4)
                        if case_4:
                            temp_new_score = 4.6
                            whois_null = True

                        else:
                            temp_new_score = (case_1 * 0.3 + (not case_1) * 2) \
                                             * (case_2 * 0.5 + (not case_2) * 3) \
                                             * (case_3 * 0.5 + (not case_3) * 4)

                        new_score = max(new_score, temp_new_score)

                    # der maximale score wird bestimmt und als indication_value eingesetzt.
                    indication_value = max(changed_score, remove_score, new_score)
                    type_score = indication_value * basis_score

                elif type == 'TEXT':
                    basis_score = 1
                    indication_value = 1.2
                type_score = basis_score * indication_value

            elif unscored_records == previous_records:
                type_score = 0

            # Wenn bei diesem Typ ein neuer höchst Score Wert erreicht wird wird dieser als neuer Scorewert gewählt
            # und der Typ vorne an die  scored_type angefügt

            # Falls es keine WHOis Informatinen gab wird dies zusätzlich kenntlich gemacht.
            if whois_null:
                type = type + ' no WHOis Info'

            if type_score > score:
                score = type_score
                if scored_type == 'No_Score':
                    scored_type = type
                else:
                    scored_type = type + ', ' + scored_type
            # Ist der wert kleiner aber es wurde ein Score größer 1 erreicht wird der typ hinten angefügt.
            elif type_score > 1:
                scored_type = scored_type + ', ' + type

        if score > 10:
            score = 10
        return round(score, 2), scored_type

    # Mit write_score wird der scoring_value und scoring_reason
    # zu einer Domainquerry mit fqdn und query_time in die DB geschrieben.
    def write_score(self, fqdn, query_time, scoring_value, scoring_reason):

        if not self.db_connection.connected:
            self.db_connection.connect()
            logger_scheduler.info('successfully established database connection')
        conn = self.db_connection.conn

        try:
            # Cursor wird erstellt
            cur = conn.cursor()
            # Update auf eine Domainquery
            postgres_update_query = f'UPDATE domain_query ' \
                                    f'SET  scoring_value = {scoring_value} , scoring_reason = \'{scoring_reason}\'' \
                                    f'WHERE fqdn = \'{fqdn}\' and query_time = \'{query_time}\';'

            cur.execute(postgres_update_query)

            conn.commit()
            # Cursor schließen
            cur.close()

            logger_scheduler.info(f'Scorer: successfully wrote Score for {fqdn} {query_time}')
        except (Exception, psycopg2.DatabaseError) as error:

            logger_scheduler.error(f'Scorer write_score: database error occurred: {error}')
            raise error

            # get_unscored_domainqueries erzeugt eine Liste mit allen nicht bewerteten Domainqueries und gibt dies aus.
            # Spalten der Liste (fqdn, query_time), sortiert nach query_time

    def get_unscored_domainqueries(self):

        unscored_domainqueries = []

        if not self.db_connection.connected:
            self.db_connection.connect()
            logger_scheduler.info('Scorer.get_unscored_domainqueries: successfully established new database connection')
        conn = self.db_connection.conn

        try:
            # Cursor wird erstellt
            cur = conn.cursor()
            # Select von allen Domainquerrys die noch nicht gescored wurden (wert=-1).
            postgres_select_query = 'SELECT domain_query.query_time, domain_query.fqdn ' \
                                    'FROM domain_query ' \
                                    'WHERE ' \
                                    'domain_query.scoring_value = -1 ' \
                                    'ORDER BY ' \
                                    'domain_query.query_time ASC;'

            cur.execute(postgres_select_query)
            unscored_domainqueries = cur.fetchall()

            # Cursor schließen
            cur.close()
            logger_scheduler.info(f'Scorer.get_unscored_domainqueries: successfully'
                                  f' extracted {len(unscored_domainqueries)} unsored domains from the database')
        except psycopg2.DatabaseError as error:
            logger_scheduler.error(f'Scorer.get_unscored_domainqueries: database error occurred: {error} ')
            raise error
        except Exception as error:
            logger_scheduler.error(f'Scorer.get_unscored_domainqueries: Error occurred: {error} ')
            raise error

        return unscored_domainqueries

    # get_all_domainqueries erzeugt eine Liste mit allen Domainqueries und gibt dies aus.
    # Spalten der Liste (fqdn, query_time), sortiert nach query_time
    def get_all_domainqueries(self):

        all_domainqueries = []

        if not self.db_connection.connected:
            self.db_connection.connect()
            logger_scheduler.info('successfully established database connection')
        conn = self.db_connection.conn

        try:
            # Cursor wird erstellt
            cur = conn.cursor()
            # Select von allen Domainsquerrys.
            postgres_select_query = 'SELECT domain_query.query_time, domain_query.fqdn ' \
                                    'FROM domain_query ' \
                                    'ORDER BY ' \
                                    'domain_query.query_time ASC;'
            cur.execute(postgres_select_query)
            all_domainqueries = cur.fetchall()
            # Cursor schließen
            cur.close()
            logger_scheduler.info(
                f'Scorer.get_all_domainqueries: successfully extracted'
                f' {len(all_domainqueries)} unsored domains from the database')

        except psycopg2.DatabaseError as error:
            logger_scheduler.error(f'Scorer.get_unscored_domainqueries: database error occurred: {error} ')
            raise error
        except Exception as error:
            logger_scheduler.error(f'Scorer.get_unscored_domainqueries: Error occurred: {error} ')
            raise error

        return all_domainqueries

    # get_previous_domainquerry gibt zu einer Domainquerry (fqdn und query_time)  die Vorgänger Domainquerry zurück.
    def get_previous_domainquerry(self, fqdn, query_time):

        if not self.db_connection.connected:
            self.db_connection.connect()
            logger_scheduler.info('Scorer.getPreviousDomainquerry: successfully established database connection')
        conn = self.db_connection.conn

        try:
            # Cursor wird erstellt
            cur = conn.cursor()
            # Select von allen Domains die nach dem fromeDatetime liegen.
            postgres_select_query = f'SELECT domain_query.query_time, domain_query.fqdn ' \
                                    f'FROM domain_query ' \
                                    f'WHERE ' \
                                    f'domain_query.fqdn = \'{fqdn}\' and domain_query.query_time < \'{query_time}\' ' \
                                    f'ORDER BY domain_query.query_time DESC LIMIT 1;'
            cur.execute(postgres_select_query)

            previous_domainquerry = cur.fetchone()

            # Cursor schließen
            cur.close()
            logger_scheduler.info(
                'Scorer.getPreviousDomainquerry: successfully extracted previous Doaminquerry from the database')

        except psycopg2.DatabaseError as error:
            logger_scheduler.error(f'Scorer.get_unscored_domainqueries: database error occurred: {error} ')
            raise error
        except Exception as error:
            logger_scheduler.error(f'Scorer.get_unscored_domainqueries: Error occurred: {error} ')
            raise error

        return previous_domainquerry

    def get_record(self, type, fqdn, query_time):

        if not self.db_connection.connected:
            self.db_connection.connect()
            logger_scheduler.info('Scorer.getARecords: successfully established database connection')
        conn = self.db_connection.conn

        try:
            # Cursor wird erstellt
            cur = conn.cursor()

            if type == 'NS':
                postgres_select_query = f'SELECT ns_record.ns, ns_record.ttl ' \
                                        f'FROM ns_record ' \
                                        f'WHERE ns_record.fqdn = \'{fqdn} \' ' \
                                        f'and ns_record.query_time = \'{query_time}\';'

            elif type == 'MX':
                postgres_select_query = f'SELECT mx_record.host_name, mx_record.preference, mx_record.ttl ' \
                                        f'FROM mx_record ' \
                                        f'WHERE ' \
                                        f'mx_record.fqdn = \'{fqdn}\' ' \
                                        f'and mx_record.query_time = \'{query_time}\';'

            elif type == 'IPV4':
                postgres_select_query = f'SELECT ipv4_whois_query.ipv4_address, ipv4_whois_query.phone, ' \
                                        f'ipv4_whois_query.person, ipv4_whois_query.organisation, ' \
                                        f'ipv4_whois_query.cidr_subnet, ipv4_whois_query.country '\
                                        f'FROM ipv4_whois_query ' \
                                        f'WHERE ' \
                                        f'ipv4_whois_query.fqdn = \'{fqdn} \' '\
                                        f'and ipv4_whois_query.query_time = \'{query_time}\';'
            elif type == 'IPV6':
                postgres_select_query = f'SELECT ipv6_whois_query.ipv6_address, ipv6_whois_query.phone, ' \
                                        f'ipv6_whois_query.person, ipv6_whois_query.organisation, ' \
                                        f'ipv6_whois_query.cidr_subnet, ipv6_whois_query.country '\
                                        f'FROM ipv6_whois_query ' \
                                        f'WHERE ' \
                                        f'ipv6_whois_query.fqdn = \'{fqdn}\' ' \
                                        f'and ipv6_whois_query.query_time = \'{query_time}\';'
            elif type == 'TEXT':
                postgres_select_query = f'SELECT text_record.text, text_record.ttl ' \
                                        f'FROM text_record ' \
                                        f'WHERE ' \
                                        f'text_record.fqdn = \'{fqdn}\' ' \
                                        f'and text_record.query_time = \'{query_time}\';'

            else:
                raise Exception('Kein gülitger Typ an scorer.get_record übergeben.')

            cur.execute(postgres_select_query)

            records = cur.fetchall()

            # Cursor schließen
            cur.close()
            logger_scheduler.info(
                f'Scorer.get_records: successfully extracted {len(records)} {type} records from the database')

        except psycopg2.DatabaseError as error:
            logger_scheduler.error(f'Scorer.get_unscored_domainqueries: database error occurred: {error} ')
            raise error
        except Exception as error:
            logger_scheduler.error(f'Scorer.get_unscored_domainqueries: Error occurred: {error} ')
            raise error

        return records
