import requests
import threading
from queue import Queue
import time
from connection import Connection
import dns.resolver
from domainquery import Domainquery

# Initialisierung der subdomain Menge 
subdomain_set = set()

# Parallel ausgeführte Funktion, 
# die alle 5 millisekunden mögliche subdomains sucht
# und bei gefundenen domains sie in eine Menge schreibt.
# fqdn = domain zu der subdomains gesucht werden sollen
# tid = thread id


def scan_subdomains(fqdn, tid, begin, end, subdomains):
    global subdomain_set
   
    for i in range(begin, end):
        # scan die subdomain
        url = f"{subdomains[i]}.{fqdn}"
        time.sleep(0.05)
        try:
            dns.resolver.resolve(url, 'A')
        except:
            pass
        else:
            subdomain_set.add(url)


def find_subdomains_dns(fqdn, n_threads, subdomains):
    """ Funktion die mit Hilfe von Multithreading die Liste
    von möglichen Subdomains ab arbeitet
    @param sting fqdn: gibt den FQDN an zu welchem Subdomains gesucht werden sollen.
    @param int n_threads: menge der threads die an diesem Problem arbeiten.
    @param list subdomains: liste von möglichen subdomains die geprüft werden sollen
    """
    global subdomain_set
    subdomain_set = set()
    begin, end, chunk = 0, 0, 0
    thread_list = []
    overhead = len(subdomains) % n_threads
    chunk = int(len(subdomains) / n_threads)
    """jeder thread bekommt seinen anteil an zu prüfenden domains"""
    for tid in range(n_threads):
        if(overhead != 0):
            end = begin + chunk + 1
            overhead -= 1
        else: 
            end = begin + chunk
        worker = threading.Thread(target=scan_subdomains, args=(fqdn, tid, begin, end, subdomains))
        thread_list.append(worker)
        worker.start()
        begin = end

    for thread in thread_list:
        thread.join()
    return subdomain_set
