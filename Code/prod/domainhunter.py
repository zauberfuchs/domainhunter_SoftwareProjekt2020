from importer import Importer
from connection import Connection
import dns.resolver
import multiprocessing
from cli import Cli
from scheduler import Scheduler

# Hauptprogramm der die CLI startet mit einer Datenbank Connection 
# und einem Scheduler Objekt
def main():

    cli = Cli(Connection(), Scheduler())
    cli.start()
    
main()