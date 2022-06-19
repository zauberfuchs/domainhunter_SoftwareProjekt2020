import os
import time
from ipwhoisquery import IPWhoIsQuery

##################################################################################################################
###                                               CLASSES                                                      ### 
##################################################################################################################

# Hier folgen die verschiedenen Record Klassen
# Vorgabe das jeder Record eine TTL besitzen muss!


class Record():
    def __init__(self, ttl):
        self.ttl = ttl


class MXRecord(Record):
    def __init__(self, ttl, host_name, preference):
        self.ttl = ttl
        self.host_name = host_name
        self.preference = preference


class ARecord(Record):
    def __init__(self, ttl, ip_v4, tld):
        self.ttl = ttl
        self.ipV4 = ip_v4
        self.whoIsQuery = IPWhoIsQuery(ip_v4, tld)


class AAAARecord(Record):
    def __init__(self, ttl, ip_v6, tld):
        self.ttl = ttl
        self.ipV6 = ip_v6
        self.whoIsQuery = IPWhoIsQuery(ip_v6, tld)


class NSRecord(Record):
    def __init__(self, ttl, ns_domain):
        self.ttl = ttl
        self.nsDomain = ns_domain


class TXTRecord(Record):
    def __init__(self, ttl, txt):
        self.ttl = ttl
        self.txt = txt
