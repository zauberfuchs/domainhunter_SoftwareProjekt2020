import os   # Für Shell Befehle benötigt
import re   # REGEX für den Parser

class IPWhoIsQuery:


    ##############################################################################################################
    #                                       Konstruktor                                                          #
    ##############################################################################################################

    def __init__(self, ip, tld):  # ip = A Record vom FQDN, tld = Top Level Domain

        ### ARIN verwaltete Domains besitzen eine Uppercase Formatierung und müssen einzeln verwaltet werden ###
        arin_format = ['.gov', '.kr', '.au', '.br', '.mil', '.uk']

        self.ip = ip
        result = self.whoIsQuery(ip)

        ### TLDś die ihre whois Daten im ARIN Format verwalten ###
        if tld in arin_format:

            ### Falls ein Parser kein Ergebnis liefert, wird gewechselt ###
            if self.phoneParserARIN(result) != set():
                self.phone = self.phoneParserARIN(result)
            elif self.phoneParser(result) != set():
                self.phone = self.phoneParser(result)
            else:
                self.phone = 'null'

            if self.cidrParserARIN(result) != set():
                self.cidr = self.cidrParserARIN(result)
            elif self.cidrParser(result) != set():
                self.cidr = self.cidrParser(result)
            else:
                self.cidr = 'null'

            if self.organisationParserARIN(result) != set():
                self.organisation = self.organisationParserARIN(result)
            elif self.organisationParser(result) != set():
                self.organisation = self.organisationParser(result)
            else:
                self.organisation = 'null'

            if self.personParserARIN(result) != set():
                self.person = self.personParserARIN(result)
            elif self.personParser(result) != set():
                self.person = self.personParser(result)
            else:
                self.person = 'null'

        ### Alle weiteren Domains werden über diese allgemeingültige Formatierung behandelt ###
        else:

            ### Falls ein Parser kein Ergebnis liefert, wird gewechselt ###
            if self.phoneParser(result) != set():
                self.phone = self.phoneParser(result)
            elif self.phoneParserARIN(result) != set():
                self.phone = self.phoneParserARIN(result)
            else:
                self.phone = 'null'

            if self.cidrParser(result) != set():
                self.cidr = self.cidrParser(result)
            elif self.cidrParserARIN(result) != set():
                self.cidr = self.cidrParserARIN(result)
            else:
                self.cidr = 'null'

            if self.organisationParser(result) != set():
                self.organisation = self.organisationParser(result)
            elif self.organisationParserARIN(result) != set():
                self.organisation = self.organisationParserARIN(result)
            else:
                self.organisation = 'null'

            if self.personParser(result) != set():
                self.person = self.personParser(result)
            elif self.personParserARIN(result) != set():
                self.person = self.personParserARIN(result)
            else:
                self.person = 'null'


    ##############################################################################################################
    #                                       ARIN-Format Parser                                                   #
    ##############################################################################################################

    def phoneParserARIN(self, stringQuery):                     # stringQuery = Ergebnis der def whoIsQuery() s.u.
        result = re.findall('(Phone:.*)', stringQuery)          # REGEX Check auf gesamten whois String
        for i, s in enumerate(result):                          # Iteration durch Liste
            result[i] = str(result[i]).replace(" ", "")         # Führende + enthaltene Whitespaces entfernen
            result[i] = str(result[i])[6:]                      # Bezeichnung / Zeilenanfang entfernen
        result = list(dict.fromkeys(result))                    # Duplikate entfernen
        return '#'.join(result)                                  # Return: Kombinierter String aus der Liste

    def cidrParserARIN(self, stringQuery):
        result = re.findall('(CIDR:.*)', stringQuery)
        for i, s in enumerate(result):
            result[i] = str(result[i]).replace(" ", "")
            result[i] = str(result[i])[5:]
        result = list(dict.fromkeys(result))
        return '#'.join(result)

    def organisationParserARIN(self, stringQuery):
        result = re.findall('(Organization:.*)', stringQuery)
        for i, s in enumerate(result):
            result[i] = str(result[i]).replace(" ", "")
            result[i] = str(result[i])[13:]
        result = list(dict.fromkeys(result))
        return '#'.join(result)

    def personParserARIN(self, stringQuery):
        result = re.findall('(Person:.*)', stringQuery)
        for i, s in enumerate(result):
            result[i] = str(result[i]).replace(" ", "")
            result[i] = str(result[i])[7:]
        result = list(dict.fromkeys(result))
        return '#'.join(result)

    ##############################################################################################################
    #                               RIPE / IANA -Format Parser                                                   #
    ##############################################################################################################

    def phoneParser(self, stringQuery):                     # stringQuery = Ergebnis der def whoIsQuery() s.u.
        result = re.findall('(phone:.*)', stringQuery)          # REGEX Check auf gesamten whois String
        for i, s in enumerate(result):                          # Iteration durch Liste
            result[i] = str(result[i]).replace(" ", "")         # Führende + enthaltene Whitespaces entfernen
            result[i] = str(result[i])[6:]                      # Bezeichnung / Zeilenanfang entfernen
        result = list(dict.fromkeys(result))                    # Duplikate entfernen
        return '#'.join(result)                                 # Return: Kombinierter String aus der Liste

    def cidrParser(self, stringQuery):
        result = re.findall('(inetnum:.*)', stringQuery)
        for i, s in enumerate(result):
            result[i] = str(result[i]).replace(" ", "")
            result[i] = str(result[i])[8:]
        result = list(dict.fromkeys(result))
        return '#'.join(result)

    def organisationParser(self, stringQuery):
        result = re.findall('(mnt-by:.*)', stringQuery)
        for i, s in enumerate(result):
            result[i] = str(result[i]).replace(" ", "")
            result[i] = str(result[i])[7:]
        result = list(dict.fromkeys(result))
        return '#'.join(result)

    def personParser(self, stringQuery):
        result = re.findall('(person:.*)', stringQuery)
        for i, s in enumerate(result):
            result[i] = str(result[i]).replace(" ", "")
            result[i] = str(result[i])[7:]
        result = list(dict.fromkeys(result))
        return '#'.join(result)

    ##############################################################################################################
    #                                       Shell Query                                                          #
    ##############################################################################################################

    def whoIsQuery(self, ip):                                   # Führt den Shell Befehl aus
        command = 'whois ' + ip
        process = os.popen(command)
        result = str(process.read())
        result.encode(encoding='utf-8', errors='ignore')
        return result

domain = IPWhoIsQuery('91.221.59.45', '.de')
print(domain.cidr)
print(domain.ip)
print(domain.person)
print(domain.organisation)
