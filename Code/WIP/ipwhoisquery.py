import re           # REGEX für den Parser
import subprocess   # Für Shell Befehle benötigt
from logger import logger_scheduler


class IPWhoIsQuery:

    ##############################################################################################################
    #                                       Konstruktor                                                          #
    ##############################################################################################################

    def __init__(self, ip, tld):  # ip = A Record vom FQDN, tld = Top Level Domain

        # Einzelne TLD´s die nachweislich initial besser über den ARIN Parser verwaltet werden sollten
        arin_format = ['gov', 'kr', 'au', 'br', 'mil', 'uk', 'lt']

        self.ip = ip
        raw_data = self.whois_query(ip)
        raw = raw_data.replace('"', '')
        self.raw = raw.replace('\'', '')

        # TLDś die ihre whois Daten im ARIN Format verwalten
        if tld in arin_format:

            # Falls ein Parser kein Ergebnis liefert, wird gewechselt
            if self.phone_parser_arin(raw_data):
                self.phone = self.phone_parser_arin(raw_data)
            elif self.phone_parser(raw_data):
                self.phone = self.phone_parser(raw_data)
            else:
                self.phone = 'null'

            if self.cidr_parser_arin(raw_data):
                self.cidr = self.cidr_parser_arin(raw_data)
            elif self.cidr_parser(raw_data):
                self.cidr = self.cidr_parser(raw_data)
            else:
                self.cidr = 'null'

            if self.organisation_parser_arin(raw_data):
                self.organisation = self.organisation_parser_arin(raw_data)
            elif self.organisation_parser(raw_data):
                self.organisation = self.organisation_parser(raw_data)
            else:
                self.organisation = 'null'

            if self.person_parser_arin(raw_data):
                self.person = self.person_parser_arin(raw_data)
            elif self.person_parser(raw_data):
                self.person = self.person_parser(raw_data)
            else:
                self.person = 'null'

            if self.country_parser_arin(raw_data):
                self.country = self.country_parser_arin(raw_data)
            elif self.country_parser(raw_data):
                self.country = self.country_parser(raw_data)
            else:
                self.country = 'null'

        # Alle weiteren Domains werden zuerst über diese allgemeingültige Formatierung behandelt
        else:

            # Falls ein Parser kein Ergebnis liefert, wird gewechselt
            if self.phone_parser(raw_data):
                self.phone = self.phone_parser(raw_data)
            elif self.phone_parser_arin(raw_data):
                self.phone = self.phone_parser_arin(raw_data)
            else:
                self.phone = 'null'

            if self.cidr_parser(raw_data):
                self.cidr = self.cidr_parser(raw_data)
            elif self.cidr_parser_arin(raw_data):
                self.cidr = self.cidr_parser_arin(raw_data)
            else:
                self.cidr = 'null'

            if self.organisation_parser(raw_data):
                self.organisation = self.organisation_parser(raw_data)
            elif self.organisation_parser_arin(raw_data):
                self.organisation = self.organisation_parser_arin(raw_data)
            else:
                self.organisation = 'null'

            if self.person_parser(raw_data):
                self.person = self.person_parser(raw_data)
            elif self.person_parser_arin(raw_data):
                self.person = self.person_parser_arin(raw_data)
            else:
                self.person = 'null'

            if self.country_parser(raw_data):
                self.country = self.country_parser(raw_data)
            elif self.country_parser_arin(raw_data):
                self.country = self.country_parser_arin(raw_data)
            else:
                self.country = 'null'

            if self.country == 'null' and self.person == 'null' and self.organisation == 'null' \
                    and self.cidr == 'null' and self.phone == 'null':
                logger_scheduler.info('whois: all null, probably because of block by RIPE')

    ##############################################################################################################
    #                                       ARIN-Format Parser                                                   #
    ##############################################################################################################

    def phone_parser_arin(self, string_query):                     # stringQuery = Ergebnis der def whois_query() s.u.
        result = re.findall('(Phone:.*)', string_query)          # REGEX Check auf gesamten whois String
        for i, s in enumerate(result):                          # Iteration durch Liste
            result[i] = str(result[i]).replace(" ", "")         # Führende + enthaltene Whitespaces entfernen
            result[i] = str(result[i])[6:]                      # Bezeichnung / Zeilenanfang entfernen
        result = list(dict.fromkeys(result))                    # Duplikate entfernen
        return '#'.join(result)                                 # Return: Kombinierter String aus der Liste

    def cidr_parser_arin(self, string_query):
        result = re.findall('(CIDR:.*)', string_query)
        for i, s in enumerate(result):
            result[i] = str(result[i]).replace(" ", "")
            result[i] = str(result[i])[5:]
        result = list(dict.fromkeys(result))
        return '#'.join(result)

    def organisation_parser_arin(self, string_query):
        result = re.findall('(Organization:.*)', string_query)
        for i, s in enumerate(result):
            result[i] = str(result[i]).replace(" ", "")
            result[i] = str(result[i])[13:]
        result = list(dict.fromkeys(result))
        return '#'.join(result)

    def person_parser_arin(self, string_query):
        result = re.findall('(Person:.*)', string_query)
        for i, s in enumerate(result):
            result[i] = str(result[i]).replace(" ", "")
            result[i] = str(result[i])[7:]
        result = list(dict.fromkeys(result))
        return '#'.join(result)

    # Es wird stets der zuletzt gefundene Countrycode gespeichert, damit nicht fälschlicherweise der Countrycode
    # vom Netz z.B. RIPE verwendet wird
    def country_parser_arin(self, string_query):
        result = re.findall('(Country:.*)', string_query)
        for i, s in enumerate(result):
            result[i] = str(result[i]).replace(" ", "")
            result[i] = str(result[i])[8:]
        result = list(dict.fromkeys(result))

        # Nur letztes Element in der Liste ist relevant
        if result:
            last_item = result[-1]
        else:
            last_item = None

        return last_item

    ##############################################################################################################
    #                               RIPE / IANA -Format Parser                                                   #
    ##############################################################################################################

    def phone_parser(self, string_query):                         # stringQuery = Ergebnis der def whois_query() s.u.
        result = re.findall('(phone:.*)', string_query)          # REGEX Check auf gesamten whois String
        for i, s in enumerate(result):                          # Iteration durch Liste
            result[i] = str(result[i]).replace(" ", "")         # Führende + enthaltene Whitespaces entfernen
            result[i] = str(result[i])[6:]                      # Bezeichnung / Zeilenanfang entfernen
        result = list(dict.fromkeys(result))                    # Duplikate entfernen
        return '#'.join(result)                                 # Return: Kombinierter String aus der Liste

    def cidr_parser(self, string_query):
        result = re.findall('(inetnum:.*)', string_query)
        for i, s in enumerate(result):
            result[i] = str(result[i]).replace(" ", "")
            result[i] = str(result[i])[8:]
        result = list(dict.fromkeys(result))
        return '#'.join(result)

    def organisation_parser(self, string_query):
        result = re.findall('(mnt-by:.*)', string_query)
        for i, s in enumerate(result):
            result[i] = str(result[i]).replace(" ", "")
            result[i] = str(result[i])[7:]
        result = list(dict.fromkeys(result))
        return '#'.join(result)

    def person_parser(self, string_query):
        result = re.findall('(person:.*)', string_query)
        for i, s in enumerate(result):
            result[i] = str(result[i]).replace(" ", "")
            result[i] = str(result[i])[7:]
        result = list(dict.fromkeys(result))
        return '#'.join(result)

    # Es wird stets der zuletzt gefundene Countrycode gespeichert, damit nicht faelschlicherweise der Countrycode
    # von z.B. RIPE verwendet wird
    def country_parser(self, string_query):
        result = re.findall('(country:.*)', string_query)
        for i, s in enumerate(result):
            result[i] = str(result[i]).replace(" ", "")
            result[i] = str(result[i])[8:]
        result = list(dict.fromkeys(result))

        # Nur letztes Element in der Liste ist relevant
        if result:
            last_item = result[-1]
        else:
            last_item = None

        return last_item

    ##############################################################################################################
    #                                       Shell Query                                                          #
    ##############################################################################################################

    # Führt den Shell Befehl aus
    def whois_query(self, ip):
        result = ''
        query = subprocess.Popen(['whois', ip], stdout=subprocess.PIPE, encoding='utf-8', errors='ignore')
        unformatted_result = query.stdout.readlines()
        for line in unformatted_result:
            result += str(line)
            result = result.replace('\\n', '\n')
        return result
