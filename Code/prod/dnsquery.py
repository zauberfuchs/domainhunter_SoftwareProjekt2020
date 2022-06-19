### Dieses module benötigt die Bibliothek dnspython, https://www.dnspython.org/

import os
import dns.resolver
import re
from logger import logger_scheduler
from records import MXRecord, NSRecord, AAAARecord, ARecord, TXTRecord

##################################################################################################################
#                                                  DNS Resolve                                                   # 
##################################################################################################################

# Methode um eine liste von MX Records zu einer URL zu erstellen
def create_mx(fqdn, record_dict, resolver):
    record_dict['MX'] = []
    answers = resolver.resolve(fqdn, 'MX')
    for rdata in answers:
        record_dict['MX'].append(MXRecord(answers.rrset.ttl, rdata.exchange, rdata.preference))

# Methode um eine liste von NS Records zu einer URL zu erstellen
def create_ns(fqdn, record_dict, resolver):
    record_dict['NS'] = []
    answers = resolver.resolve(fqdn, 'NS')
    for rdata in answers:
        record_dict['NS'].append(NSRecord(answers.rrset.ttl, rdata.target))

# Methode um eine liste von A Records zu einer URL zu erstellen
def create_a(fqdn, record_dict, resolver):
    record_dict['A'] = []
    #cloudflareResolver = dns.resolver.Resolver()
    #cloudflareResolver.nameservers = ['1.1.1.1']
    answers = resolver.resolve(fqdn, 'A')
    for rdata in answers:
        record_dict['A'].append(ARecord(answers.rrset.ttl, rdata.address, (fqdn).split('.')[-1]))

# Methode um eine liste von AAAA Records zu einer URL zu erstellen
def create_aaaa(fqdn, record_dict, resolver):
    record_dict['AAAA'] = []
    answers = resolver.resolve(fqdn, 'AAAA')
    for rdata in answers:
        record_dict['AAAA'].append(AAAARecord(answers.rrset.ttl, rdata.address, (fqdn).split('.')[-1]))

# Methode um eine liste von TXT Records zu einer URL zu erstellen
def create_txt(fqdn, record_dict, resolver):
    record_dict['TXT'] = []
    answers = resolver.resolve(fqdn, 'TXT')
    regex = re.compile(r"^'b$|'", re.IGNORECASE)
    for rdata in answers:
        record_dict['TXT'].append(TXTRecord(answers.rrset.ttl, regex.sub("", str(rdata.strings[0]))))

##################################################################################################################
#                                                  Record builder                                                # 
##################################################################################################################

# setzt eine DNS query ab und baut aus den antworten das richtige Objekt zusammen
# fqdn = fqdn auf die die DNS Query ausgeführt werden soll
# record_dict = Dictonary mit den records
# m = variable für die jede methode ausgeführt wird
# dns.resolver.NoAnswer muss gefangen werden falls ein bestimmter record nicht vorhanden ist
# folgende exceptions werden hier gefangen weil sie durchaus vorkommen können, lediglich die
# dns.resolver.timeout exception wird weiter oben gefangen da sie unsere daten verfälschen würde
def create_records(fqdn, record_dict, resolver):
    for m in [create_mx, create_ns, create_a, create_aaaa, create_txt]:
        try:
            m(fqdn, record_dict, resolver)
        except dns.resolver.NoAnswer as error:
            logger_scheduler.error('dnsquery: dns.resolver.NoAnswer: ' + str(error))
            pass
        except dns.resolver.NXDOMAIN as error:
            logger_scheduler.error('dnsquery: dns.resolver.NXDOMAIN: ' + str(error))
            pass

# recordDict = Dictonary das übergeben wird um es zu befüllen
# gibt das dictonary mit den records zurück zum fqdn
def change_dns(fqdn):
    resolver = dns.resolver.Resolver()
    resolver.nameservers = ['1.1.1.1'] # using Cloudflare DNS
    nameservers = []
    try:
        result = resolver.resolve(fqdn, 'NS')
        nameservers = [ns.to_text() for ns in result]
    except dns.resolver.NoAnswer as error:
        logger_scheduler.error('dnsquery: dns.resolver.NoAnswer: ' + str(error))
        pass
    except dns.resolver.NXDOMAIN as error:
        logger_scheduler.error('dnsquery: dns.resolver.NXDOMAIN: ' + str(error))
        pass
    
    nameservers.append('1.1.1.1')
    return nameservers

def get_records(fqdn):
    record_dict = {}
    resolver = dns.resolver.Resolver()
    resolver.nameservers = change_dns(fqdn)
    create_records(fqdn, record_dict, resolver)
    return record_dict
