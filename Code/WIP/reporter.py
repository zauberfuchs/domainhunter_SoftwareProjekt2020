#from connection import Connection
from connection import Connection
from create_pdf import PDF
from create_csv import CsvOut
from tabulate import tabulate
import csv

header = '##################################################################################################################\n'\
                '###                                               Report                                                       ###\n'\
                '##################################################################################################################\n'


class Reporter():

    def __init__(self, db_connection):
        self.connection = db_connection
        self.filter_fqdn = None
        self.start_date = None
        self.end_date = None
        self.start_score = None
        self.end_score = None

    def create_bulk_report(self, filter_fqdn, start_date, end_date, start_score, end_score, display_type):
        # create a cursor
        cur = self.connection.conn.cursor()
       
        # Gibt domain_querys aus.
        if(filter_fqdn == '*'):
            postgres_select_query = 'SELECT * FROM domain_query WHERE query_time BETWEEN \'' + str(start_date) + '\'' \
                                    + ' AND \'' + str(end_date) + '\'' + ' AND scoring_value BETWEEN \'' \
                                    + str(start_score) + '\'' + ' AND \'' + str(end_score) + '\'ORDER BY query_time;'
        else:
            postgres_select_query = 'SELECT * FROM domain_query WHERE fqdn = ''\'' + filter_fqdn + '\'' \
                                    + ' AND query_time BETWEEN \'' + str(start_date) + '\'' + ' AND \'' \
                                    + str(end_date) + '\'' + ' AND scoring_value BETWEEN \'' + str(start_score) \
                                    + '\'' + ' AND \'' + str(end_score) + '\'ORDER BY query_time;'
        cur.execute(postgres_select_query)
        rows = cur.fetchall()
        get_table_schema = "SELECT column_name FROM information_schema.columns WHERE table_name = 'domain_query';"
        cur.execute(get_table_schema)
        schema = cur.fetchall()
        
        # Fuegt die schema Tabelle mit der query Ergebnis zusammen
        schemaorder = [[]]
        for datum in schema:
            schemaorder[0].append(datum[0])
        # Object Liste in String Liste
        objecttable = schemaorder + rows
        table =[[]]
        for rows in objecttable:
            puffer = []
            for row in rows:
                puffer.append(str(row))
            table.append(puffer)

        if(display_type == '1'):
            csv_reporter = CsvOut(table)
            csv_reporter.export_csv()
        elif(display_type == '2'):
            pdf_reporter = PDF()
            pdf_reporter.big_report(table)
        else:
            print('###########################################################################################\n' +
                '###                                      Report                                         ###\n'
                '###########################################################################################')            
            print(tabulate(table, headers="firstrow" ,tablefmt="psql"))
