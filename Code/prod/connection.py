#!/usr/bin/python
import psycopg2
from config import config

class Connection:



    def __init__(self):
        # Die Variable conn speichert die jeweilige Datenbank Verbindung des Objekts.
        self.conn = None
        self.connected = False


    # Um eine Verbindung aufzubauen wird die connect Methode ausgeführt. Wird eine Verbidungun ordnungsgemäß aufgebaut gibt es einen Rückgabewert der True ist. Gibt es eine Fehler oder die Verbindung war schon aufgebaut wird False zurückgegeben.

    def connect(self):
        """ Connect to the PostgreSQL database server """
        connected = False
        try:
            # read connection parameters
            params = config()

            # connect to the PostgreSQL server
            print('Connecting to the PostgreSQL database...')
            self.conn = psycopg2.connect(**params)
            connected = True

        except (Exception, psycopg2.DatabaseError) as error:
            print("Beim Aufbau der Datenbank Verbindung kam es zu folgendem Fehler:\n ")
            print(error)
            self.conn.close()
            connected = False
        finally:
            self.connected=connected
            return connected

    # Um eine Verbindung abzubauen wird die close Methode ausgeführt. Wird eine Verbidungun ordnungsgemäß abgebaut gibt es einen Rückgabewert der True ist. Gibt es eine Fehler oder die Verbindung war schon geschlossen wird False zurückgegeben.

    def disconnect (self):
        """ Connect to the PostgreSQL database server """

        closed = False
        if self.conn is not None or self.conn.closed == 0:
            self.conn.close
            closed = True
            conn = None
        self.connected = not closed
        return closed

