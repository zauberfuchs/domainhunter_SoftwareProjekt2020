import os
import re
import time
import multiprocessing
import subprocess as sp
from importer import Importer
from connection import Connection
from domain import Domain
from subdomain import find_subdomains_dns
from reporter import Reporter
from datetime import datetime, timedelta
from logger import logger_cli
import curses
import threading

##############################################################################################################
#                                       FARBEN (OPTIONAL)                                                    #
##############################################################################################################


class Colors:
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'

    ##############################################################################################################
    #                                       CLI MENU STRINGS                                                     #
    ##############################################################################################################


LOGO = '    ____                        _          __  __            __ \n' \
    '   / __ \____  ____ ___  ____ _(_)___     / / / /_  ______  / /____  _____\n' \
    '  / / / / __ \/ __ `__ \/ __ `/ / __ \   / /_/ / / / / __ \/ __/ _ \/ ___/\n' \
    ' / /_/ / /_/ / / / / / / /_/ / / / / /  / __  / /_/ / / / / /_/  __/ /    \n' \
    '/_____/\____/_/ /_/ /_/\__,_/_/_/ /_/  /_/ /_/\__,_/_/ /_/\__/\___/_/   \n'

HELP_BAR = '\nEnter any number corresponding to the menu item\nor "p" to return to the previous menu.'

MAIN_MENU = 'Main menu\n\n' \
           '1 ~ Query menu\n' \
           '2 ~ Scheduler menu\n' \
           '3 ~ Reporting\n' \
           '4 ~ Importing\n' \
           '5 ~ Status\n' \
           '6 ~ Add information to domains and domainqueries\n' \
           'x ~ Exit program\n' \
            + HELP_BAR

QUERY_MENU = 'Query menu\n\n' \
            '1 ~ Execute custom domainquery\n' \
            '2 ~ Execute subdomainfinder for a single domain\n' \
             + HELP_BAR

SCHEDULER_MENU = 'Scheduler menu\n\n' \
            '1 ~ Start scheduler\n' \
            '2 ~ Stop scheduler\n' \
            '3 ~ Set wait time\n'\
            '4 ~ Set update time\n' \
                 + HELP_BAR

REPORTING_MENU = 'Reporting\n\n' \
            '1 ~ Custom report with filters\n' \
                 + HELP_BAR

FILTER_MENU = 'Filtering\n\n' \
            '1 ~ Set custom FQDN\n' \
            '2 ~ Set start date\n' \
            '3 ~ Set end date\n' \
            '4 ~ Set start score\n' \
            '5 ~ Set end score\n' \
            '6 ~ Report with current filters\n'

IMPORTER_MENU = 'Domain import\n\n' \
             '1 ~ Single element import\n' \
             '2 ~ Bulk import via csv file\n' \
             '3 ~ Choose subdomain dictionary file\n' \
                + HELP_BAR

INDORMATION_MENU = 'Add domain / query information\n\n' \
             '1 ~ Add comment to domain\n' \
             '2 ~ Add comment to domainquery\n' \
             '3 ~ Add category to domainquery\n' \
                   + HELP_BAR

##############################################################################################################
#                                       CODE                                                                 #
##############################################################################################################


class Cli():

    def __init__(self, db_connection, scheduler):
        self.importer = None
        self.reporter = None
        self.filter = ['*',
                        str((datetime.now() + timedelta(days=-3)).strftime("%Y/%m/%d")),
                        str((datetime.now() + timedelta(days=1)).strftime("%Y/%m/%d")),
                        0,
                        10]
        self.conn = db_connection
        self.scheduler = scheduler
        self.status = 0
        self.processes = {}
        self.is_scheduling = False
        self.worker = None
        self.updates_status = False
        self.subdomain_file = 1000

        if(self.conn.connect()):
            self.importer = Importer(self.conn)
            self.reporter = Reporter(self.conn)

    def clear(self):
        os.system('clear')

    def get_current_count_domains(self):
        cur = self.conn.conn.cursor()
        postgres_select_query = 'SELECT COUNT(*) FROM domain;'
        cur.execute(postgres_select_query)
        row = cur.fetchone()
        return row[0]

    def get_current_count_domainquerys(self):
        cur = self.conn.conn.cursor()
        postgres_select_query = 'SELECT COUNT(*) FROM domain_query;'
        cur.execute(postgres_select_query)
        row = cur.fetchone()
        return row[0]

    def get_last_updated_domain(self):
        cur = self.conn.conn.cursor()
        postgres_select_query = 'SELECT fqdn, query_time from domain_query order by query_time desc;'
        cur.execute(postgres_select_query)
        row = cur.fetchone()
        return row[0]

    def add_comment_to_domain(self, domain, comment):
        cur = self.conn.conn.cursor()
        postgres_update_domain = f'UPDATE domain SET comment = \'{comment}\' WHERE fqdn = \'{domain}\';'
        cur.execute(postgres_update_domain)
        self.conn.conn.commit()

    def add_comment_to_domainquery(self, domain, comment, query_time):
        cur = self.conn.conn.cursor()
        postgres_update_domain = f'UPDATE domain_query SET comment = \'{comment}\' WHERE fqdn = \'{domain}\' AND query_time = \'{query_time}\';'
        cur.execute(postgres_update_domain)
        self.conn.conn.commit()

    def add_category_to_domainquery(self, domain, category, query_time):
        cur = self.conn.conn.cursor()
        postgres_update_domain = f'UPDATE domain_query SET category = \'{category}\' WHERE fqdn = \'{domain}\' AND query_time = \'{query_time}\';'
        cur.execute(postgres_update_domain)
        self.conn.conn.commit()

    def update_status(self):
        scheduler_status = f''
        if self.is_scheduling:
            scheduler_status = f'{Colors.GREEN}ACTIVE{Colors.END}'
        else:
            scheduler_status = f'{Colors.RED}DEACTIVATED{Colors.END}'
        status = f'Scheduler is currently: {scheduler_status} \n'\
                 f'Current domains: {self.get_current_count_domains()} \n'\
                 f'Current domainqueries: {self.get_current_count_domainquerys()} \n'\
                 f'Last updated domain: {self.get_last_updated_domain()} \n'\
                 f'{Colors.RED}["p" to return]  {Colors.END}'
        self.clear()
        print(f'{Colors.RED}{LOGO}  {Colors.END} \n{status}')
        while(self.updates_status):
            time.sleep(1)
            status = f'Scheduler is currently: {scheduler_status} \n'\
                     f'Current domains: {self.get_current_count_domains()} \n'\
                     f'Current domainqueries: {self.get_current_count_domainquerys()} \n'\
                     f'Last updated domain: {self.get_last_updated_domain()} \n'\
                     f'{Colors.RED}["p" to return]  {Colors.END}'
            self.clear()
            print(f'{Colors.RED}{LOGO}  {Colors.END} \n{status}')
            

        
    
    def query_menu_def(self, user_input):
        single_query = None
        self.status = 1

        if user_input == 'p':
            self.status = 0
            self.clear()
            self.start()

        elif user_input == '1':
            print(f'Enter the domain to be queried. [syntax: w-hs.de]{Colors.RED} ["p" to return]  {Colors.END}')
            entered_domain = input(f'{Colors.GREEN}')

            if bool(re.match('.{2,40}\.\w{2,3}', entered_domain)):
                if self.importer.validate_if_domains_in_db(entered_domain, self.importer.get_all_domains()):
                    single_query = Domain(entered_domain, False, self.conn, logger_cli)
                    single_query.update_db_record()
                    print('Domain is being queried. To view results, go the reporting menu.')
                    self.go_to_menu(3, QUERY_MENU, self.query_menu_def)
                else:
                    print('This Domain is not present in the Database')
                    self.go_to_menu(3, QUERY_MENU, self.query_menu_def)

            elif entered_domain == 'p':
                self.clear()
                print(f'{Colors.RED}  {LOGO}  {Colors.END}  \n  {QUERY_MENU}')
                self.go_to_menu(0, QUERY_MENU, self.query_menu_def)

            else:
                print(f'{Colors.RED}  Error: invalid input.  {Colors.END}')
                time.sleep(1)
                self.query_menu_def('1')

        elif user_input == '2':
            print(f'Enter the domain to be checked for subdomains. [Syntax: w-hs.de]  {Colors.RED}  ["p" to return]  {Colors.END}')
            entered_domain = input(f"{Colors.GREEN}")

            if bool(re.match('.{2,40}\.\w{2,3}', entered_domain)):
                self.importer.create_subdomains(entered_domain)    # Hier muss die Funktion zum subdomainfinder angekoppelt werden
                print('Searching for subdomains and updating database.')
                self.go_to_menu(3, QUERY_MENU, self.query_menu_def)

            elif entered_domain == 'p':
                self.go_to_menu(0, QUERY_MENU, self.query_menu_def)

            else:
                print(f'{Colors.RED}Error: invalid input. {Colors.END}')
                time.sleep(1)
                self.query_menu_def('1')

        else:
            print(f'{Colors.RED} The user input was invalid, please only use allowed characters. {Colors.END}')
            x = input()
            self.query_menu_def(x)

    def scheduler_menu_def(self, user_input):

        self.status = 2

        if user_input == 'p':
            self.status = 0
            self.clear()
            self.start()

        elif user_input == '1':
            if(self.is_scheduling):
                print('Scheduler is already running.')
            else:
                self.start_process('scheduler', self.scheduler.start)
                print('Scheduler has been started.')
                self.is_scheduling = True
            self.go_to_menu(3, SCHEDULER_MENU, self.scheduler_menu_def)

        elif user_input == '2':
            if(self.is_scheduling):
                self.stop_process('scheduler')
                print('Scheduler has been stopped.')
                self.is_scheduling = False
            else:
                print('Scheduler has to be started before it can be stopped.')
            self.go_to_menu(3, SCHEDULER_MENU, self.scheduler_menu_def)

        elif user_input == '3':
            print('\nEnter wait time for the scheduler to pause after a complete DB query in minutes. \nCurrent wait tme: ' +
                  str(self.scheduler.wait_time) + ' minutes ' + f"{Colors.RED}" + '["p" to return]' + Colors.END + '\n')
            x = input(f"{Colors.GREEN}")
            if x == 'p':
                self.go_to_menu(0, SCHEDULER_MENU, self.scheduler_menu_def)
            elif x.isdecimal():
                self.scheduler.wait_time = int(x)
                if(self.is_scheduling):
                    self.restart_process('scheduler', self.scheduler.start)
                print('Wait time set to ' + x + ' minutes.')
                self.go_to_menu(3, SCHEDULER_MENU, self.scheduler_menu_def)
            else:
                print(f"{Colors.RED}" + 'Entered value was not an integer.' + Colors.END)
                time.sleep(1)
                self.scheduler_menu_def('3')


        elif user_input == '4':
            print('\nEnter update time for a domain to not be queried again in minutes. \nCurrent update tme: ' +
                  str(self.scheduler.update_time) + ' minutes ' + f"{Colors.RED}" + '["p" to return]' + Colors.END + '\n')
            x = input(f"{Colors.GREEN}")

            if x == 'p':
                self.go_to_menu(0, SCHEDULER_MENU, self.scheduler_menu_def)

            elif x.isdecimal():
                self.scheduler.update_time = int(x)
                if(self.is_scheduling):
                    self.restart_process('scheduler', self.scheduler.start)
                print('Update time set to ' + x + ' minutes.')
                self.go_to_menu(3, SCHEDULER_MENU, self.scheduler_menu_def)

            else:
                print(f"{Colors.RED}" + 'Entered value was not an integer.' + Colors.END)
                time.sleep(1)
                self.scheduler_menu_def('4')

        else:
            print(f"{Colors.RED}" + 'The user input was invalid, please only use allowed characters.' + Colors.END)
            x = input()
            self.scheduler_menu_def(x)


    def reporting_menu_def(self, userInput):



        self.status = 3


        if userInput == 'p':
            self.status = 0
            self.clear()
            self.start()
        elif userInput == '1':
            self.clear()
            self.go_to_menu(0, f"{FILTER_MENU} \nCurrent filters:\
                             \nFQDN        = {Colors.RED}{self.filter[0]}{Colors.END}\
                             \nStart date  = {Colors.RED}{self.filter[1]}{Colors.END}   End date  = {Colors.RED}{self.filter[2]}{Colors.END}\
                             \nStart score = {Colors.RED}{self.filter[3]}{Colors.END}            End score = {Colors.RED}{self.filter[4]}{Colors.END}\
                             \n{HELP_BAR}", self.filter_menu_def)

        else:
            print(f"{Colors.RED}" + 'The user input was invalid, please only use allowed characters.' + Colors.END)
            x = input()
            self.reporting_menu_def(x)

    def filter_menu_def(self, userInput):

        self.status = 5

        if userInput == 'p':
            self.go_to_menu(0, REPORTING_MENU, self.reporting_menu_def)

        elif userInput == '1':
            self.clear()
            print('Enter the domain to be reported. Current domain: ' + str(self.filter[0]) + '\n'
                                    '[syntax: w-hs.de or * to print all domains]' + f"{Colors.RED}" +
                ' ["p" to return]' + Colors.END +'\n')
            enteredDomain = input(f"{Colors.GREEN}")
            if bool(re.match('(^(?:.{2,40}\.\w{2,3}$))|^(\*)$', enteredDomain)):
                self.filter[0] = enteredDomain
                print('New custom domain = ' + enteredDomain)
                self.go_to_menu(2, f"{FILTER_MENU} \nCurrent filters:\
                             \nFQDN        = {Colors.RED}{self.filter[0]}{Colors.END}\
                             \nStart date  = {Colors.RED}{self.filter[1]}{Colors.END}   End date  = {Colors.RED}{self.filter[2]}{Colors.END}\
                             \nStart score = {Colors.RED}{self.filter[3]}{Colors.END}            End score = {Colors.RED}{self.filter[4]}{Colors.END}\
                             \n{HELP_BAR}", self.filter_menu_def)
            elif enteredDomain == 'p':
                self.go_to_menu(0, f"{FILTER_MENU} \nCurrent filters:\
                             \nFQDN       = {Colors.RED}{self.filter[0]}{Colors.END}\
                             \nStart date  = {Colors.RED}{self.filter[1]}{Colors.END}   End date  = {Colors.RED}{self.filter[2]}{Colors.END}\
                             \nStart score = {Colors.RED}{self.filter[3]}{Colors.END}            End score = {Colors.RED}{self.filter[4]}{Colors.END}\
                             \n{HELP_BAR}", self.filter_menu_def)
            else:
                print(f"{Colors.RED}" + 'Error: invalid input.' + Colors.END)
                time.sleep(1)
                self.filter_menu_def('1')
        elif userInput == '2':
            self.clear()
            print('Enter the start date of the first query update. Current start date: ' + str(self.filter[1]) +
                                    '\n[syntax: yyyy/mm/dd]' + f"{Colors.RED}" +
                ' ["p" to return]' + Colors.END +'\n')
            enteredStartDate = input(f"{Colors.GREEN}")
            if bool(re.match('^20[0-2][0-9]/((0[1-9])|(1[0-2]))/([0-2][1-9]|3[0-1])$', enteredStartDate)):
                self.filter[1] = enteredStartDate
                print('new Start Date = ' + enteredStartDate)
                self.go_to_menu(2, f"{FILTER_MENU} \nCurrent filters:\
                             \nFQDN        = {Colors.RED}{self.filter[0]}{Colors.END}\
                             \nStart date  = {Colors.RED}{self.filter[1]}{Colors.END}   End date  = {Colors.RED}{self.filter[2]}{Colors.END}\
                             \nStart score = {Colors.RED}{self.filter[3]}{Colors.END}            End score = {Colors.RED}{self.filter[4]}{Colors.END}\
                             \n{HELP_BAR}", self.filter_menu_def)
            elif enteredStartDate == 'p':
                self.go_to_menu(0, f"{FILTER_MENU} \nCurrent filters:\
                             \nFQDN        = {Colors.RED}{self.filter[0]}{Colors.END}\
                             \nStart date  = {Colors.RED}{self.filter[1]}{Colors.END}   End date  = {Colors.RED}{self.filter[2]}{Colors.END}\
                             \nStart score = {Colors.RED}{self.filter[3]}{Colors.END}            End score = {Colors.RED}{self.filter[4]}{Colors.END}\
                             \n{HELP_BAR}", self.filter_menu_def)
            else:
                print(f"{Colors.RED}" + 'Error: invalid input.' + Colors.END)
                time.sleep(1)
                self.filter_menu_def('2')
        elif userInput == '3':
            self.clear()
            print('Enter the end date of the last query update. Current end date: ' + str(self.filter[2]) +
                                    '\n[syntax: yyyy/mm/dd]' + f"{Colors.RED}" +
                ' ["p" to return]' + Colors.END +'\n')
            entered_end_date = input(f"{Colors.GREEN}")
            if bool(re.match('^20[0-2][0-9]/((0[1-9])|(1[0-2]))/([0-2][1-9]|3[0-1])$', entered_end_date)):
                self.filter[2] = entered_end_date
                print('new End Date = ' + entered_end_date)
                self.go_to_menu(2, f"{FILTER_MENU} \nCurrent filters:\
                             \nFQDN        = {Colors.RED}{self.filter[0]}{Colors.END}\
                             \nStart date  = {Colors.RED}{self.filter[1]}{Colors.END}   End date  = {Colors.RED}{self.filter[2]}{Colors.END}\
                             \nStart score = {Colors.RED}{self.filter[3]}{Colors.END}            End score = {Colors.RED}{self.filter[4]}{Colors.END}\
                             \n{HELP_BAR}", self.filter_menu_def)
            elif entered_end_date == 'p':
                self.go_to_menu(0, f"{FILTER_MENU} \nCurrent filters:\
                             \nFQDN        = {Colors.RED}{self.filter[0]}{Colors.END}\
                             \nStart date  = {Colors.RED}{self.filter[1]}{Colors.END}   End date  = {Colors.RED}{self.filter[2]}{Colors.END}\
                             \nStart score = {Colors.RED}{self.filter[3]}{Colors.END}            End score = {Colors.RED}{self.filter[4]}{Colors.END}\
                             \n{HELP_BAR}", self.filter_menu_def)
            else:
                print(f"{Colors.RED}" + 'Error: invalid input.' + Colors.END)
                time.sleep(1)
                self.filter_menu_def('3')
        elif userInput == '4':
            self.clear()
            print('Enter the minimum score. Current start Score: ' + str(self.filter[3]) +
                                    '\n[syntax: number]' + f"{Colors.RED}" +
                ' ["p" to return]' + Colors.END +'\n')
            entered_start_score = input(f"{Colors.GREEN}")
            if bool(re.match('^(?:[0-9]|10)$', entered_start_score)):
                self.filter[3] = entered_start_score
                print('New start score = ' + entered_start_score)
                self.go_to_menu(2, f"{FILTER_MENU} \nCurrent filters:\
                             \nFQDN        = {Colors.RED}{self.filter[0]}{Colors.END}\
                             \nStart date  = {Colors.RED}{self.filter[1]}{Colors.END}   End date  = {Colors.RED}{self.filter[2]}{Colors.END}\
                             \nStart score = {Colors.RED}{self.filter[3]}{Colors.END}            End score = {Colors.RED}{self.filter[4]}{Colors.END}\
                             \n{HELP_BAR}", self.filter_menu_def)
            elif entered_start_score == 'p':
                self.go_to_menu(0, f"{FILTER_MENU} \nCurrent filters:\
                             \nFQDN        = {Colors.RED}{self.filter[0]}{Colors.END}\
                             \nStart date  = {Colors.RED}{self.filter[1]}{Colors.END}   End date  = {Colors.RED}{self.filter[2]}{Colors.END}\
                             \nStart score = {Colors.RED}{self.filter[3]}{Colors.END}            End score = {Colors.RED}{self.filter[4]}{Colors.END}\
                             \n{HELP_BAR}", self.filter_menu_def)
            else:
                print(f"{Colors.RED}" + 'Error: invalid input.' + Colors.END)
                time.sleep(1)
                self.filter_menu_def('4')
        elif userInput == '5':
            self.clear()
            print('Enter the maximum score. Current end score: ' + str(self.filter[4]) +
                                    '\n[syntax: number]' + f"{Colors.RED}" +
                ' ["p" to return]' + Colors.END +'\n')
            entered_end_score = input(f"{Colors.GREEN}")
            if bool(re.match('^(?:[0-9]|10)$', entered_end_score)):
                self.filter[4] = entered_end_score
                print('New end score = ' + entered_end_score)
                self.go_to_menu(2, f"{FILTER_MENU} \nCurrent filters:\
                             \nFQDN        = {Colors.RED}{self.filter[0]}{Colors.END}\
                             \nStart date  = {Colors.RED}{self.filter[1]}{Colors.END}   End date  = {Colors.RED}{self.filter[2]}{Colors.END}\
                             \nStart score = {Colors.RED}{self.filter[3]}{Colors.END}            End score = {Colors.RED}{self.filter[4]}{Colors.END}\
                             \n{HELP_BAR}", self.filter_menu_def)
            elif entered_end_score == 'p':
                self.go_to_menu(0, f"{FILTER_MENU} \nCurrent filters:\
                             \nFQDN        = {Colors.RED}{self.filter[0]}{Colors.END}\
                             \nStart date  = {Colors.RED}{self.filter[1]}{Colors.END}   End date  = {Colors.RED}{self.filter[2]}{Colors.END}\
                             \nStart score = {Colors.RED}{self.filter[3]}{Colors.END}            End score = {Colors.RED}{self.filter[4]}{Colors.END}\
                             \n{HELP_BAR}", self.filter_menu_def)
            else:
                print(f"{Colors.RED}" + 'Error: invalid input.' + Colors.END)
                time.sleep(1)
                self.filter_menu_def('5')
        elif userInput == '6':
            self.clear()
            print(f"{Colors.RED}" + 'Select output format\n' + '1 = csv; 2 = pdf; 3 = terminal\n' + '["p" to return]''\n')
            display_type = input(f"{Colors.GREEN}")
            if '1' == display_type:
                self.reporter.create_bulk_report(self.filter[0], self.filter[1], self.filter[2], self.filter[3], self.filter[4], '1')
                print("CSV report was created successfully.")
                self.go_to_menu(3, f"{FILTER_MENU} \nCurrent filters:\
                             \nFQDN        = {Colors.RED}{self.filter[0]}{Colors.END}\
                             \nStart date  = {Colors.RED}{self.filter[1]}{Colors.END}   End date  = {Colors.RED}{self.filter[2]}{Colors.END}\
                             \nStart score = {Colors.RED}{self.filter[3]}{Colors.END}            End score = {Colors.RED}{self.filter[4]}{Colors.END}\
                             \n{HELP_BAR}", self.filter_menu_def)
            elif '2' == display_type:
                self.reporter.create_bulk_report(self.filter[0], self.filter[1], self.filter[2], self.filter[3], self.filter[4], '2')
                print("PDF report was created successfully.")
                self.go_to_menu(3, f"{FILTER_MENU} \nCurrent filters:\
                             \nFQDN        = {Colors.RED}{self.filter[0]}{Colors.END}\
                             \nStart date  = {Colors.RED}{self.filter[1]}{Colors.END}   End date  = {Colors.RED}{self.filter[2]}{Colors.END}\
                             \nStart score = {Colors.RED}{self.filter[3]}{Colors.END}            End score = {Colors.RED}{self.filter[4]}{Colors.END}\
                             \n{HELP_BAR}", self.filter_menu_def)
            elif '3' == display_type:
                self.reporter.create_bulk_report(self.filter[0], self.filter[1], self.filter[2], self.filter[3], self.filter[4], '3')
                print(f"{Colors.RED}" + ' ["p" to return]' + Colors.END +'\n')
                display_type = input(f"{Colors.GREEN}")
                if(display_type == 'p'):
                    self.go_to_menu(3, f"{FILTER_MENU} \nCurrent filters:\
                             \nFQDN        = {Colors.RED}{self.filter[0]}{Colors.END}\
                             \nStart date  = {Colors.RED}{self.filter[1]}{Colors.END}   End date  = {Colors.RED}{self.filter[2]}{Colors.END}\
                             \nStart score = {Colors.RED}{self.filter[3]}{Colors.END}            End score = {Colors.RED}{self.filter[4]}{Colors.END}\
                             \n{HELP_BAR}", self.filter_menu_def)
                else:
                    print(f"{Colors.RED}" + 'The user input was invalid, please only use allowed characters.' + Colors.END)
                    x = input()
                    self.filter_menu_def(x)
            elif 'p' == display_type:
                self.go_to_menu(0, f"{FILTER_MENU} \nCurrent filters:\
                             \nFQDN        = {Colors.RED}{self.filter[0]}{Colors.END}\
                             \nStart date  = {Colors.RED}{self.filter[1]}{Colors.END}   End date  = {Colors.RED}{self.filter[2]}{Colors.END}\
                             \nStart score = {Colors.RED}{self.filter[3]}{Colors.END}            End score = {Colors.RED}{self.filter[4]}{Colors.END}\
                             \n{HELP_BAR}", self.filter_menu_def)
            else:
                print(f"{Colors.RED}" + 'The user input was invalid, please only use allowed characters.' + Colors.END)
                x = input()
                self.filter_menu_def(x)
        else:
            print(f"{Colors.RED}" + 'The user input was invalid, please only use allowed characters.' + Colors.END)
            x = input()
            self.filter_menu_def(x)


    def import_menue_def(self, user_input):
        domain_import = ''

        self.status = 4

        if user_input == 'p':
            self.status = 0
            self.clear()
            self.start()
        elif user_input == '1':
            self.clear()
            print('Enter the domain to be imported, append " -sd" to check for subdomains.\n'
                                    '[syntax: w-hs.de -sd] will be checked against ' + str(self.subdomain_file) + ' possible subdomains' + f"{Colors.RED}" +
                ' ["p" to return]' + Colors.END + '\n')
            entered_domain = input(f"{Colors.GREEN}")
            if bool(re.match('.{2,40}\.\w{2,3}', entered_domain)):
                if bool(re.search('-sd', entered_domain)):
                    result_list = re.split('\s', entered_domain)    # subdomainfinder mit domain hier verbinden
                    domain_import = str(result_list[0])
                    self.importer.create_domain(domain_import, True)
                    self.go_to_menu(3, IMPORTER_MENU, self.import_menue_def)
                elif not bool(re.search('(-sd)', entered_domain)):
                    domain_import = entered_domain
                    self.importer.create_domain(domain_import, False)
                    self.go_to_menu(3, IMPORTER_MENU, self.import_menue_def)
                else:
                    print(f"{Colors.RED}" + 'Error: invalid input.' + Colors.END)
                    time.sleep(1)
                    self.import_menue_def('4')
            elif entered_domain == 'p':
                self.go_to_menu(0, IMPORTER_MENU, self.import_menue_def)
            else:
                print(f"{Colors.RED}" + 'Error: invalid input.' + Colors.END)
                time.sleep(1)
                self.import_menue_def('1')

        elif user_input == '2':
            self.clear()
            print('Enter filename and path to be imported, append " -sd" to check for subdomains.\n'
                                    '[syntax: /home/user/file.csv -sd] will be checked against ' + str(self.subdomain_file) + ' possible subdomains' +
                f"{Colors.RED}" + ' ["p" to return]' + Colors.END + '\n')
            entered_file = input(f"{Colors.GREEN}")
            if (bool(re.search('-sd', entered_file)) and bool(re.match('^(\w|\n|\/)+(.csv -sd)$', entered_file))):
                result_list = (re.split('\s', entered_file))
                self.file_path = str(result_list[0])       # import mit subdomainfinder ankoppeln
                self.importer.import_from_csv(self.file_path, True)
                print('CSV import with subdomainfinder started, elements will automatically be added to the query list.')
                self.go_to_menu(3, IMPORTER_MENU, self.import_menue_def)
            elif entered_file == 'p':
                self.go_to_menu(0, IMPORTER_MENU, self.import_menue_def)
            elif bool(re.match('^(\w|\n|\/)+(.csv)$', entered_file)) and not bool(re.search('-sd', entered_file)):
                self.file_path = entered_file      # import ohne subdomainfinder ankoppeln
                self.importer.import_from_csv(self.file_path, False)
                print('CSV import started, elements will automatically be added to the query list.')
                self.go_to_menu(3, IMPORTER_MENU, self.import_menue_def)
            else:
                print(f"{Colors.RED}" + 'Error: invalid input.' + Colors.END)
                time.sleep(1)
                self.import_menue_def('2')
        elif user_input == '3':
            self.clear()
            print('Enter how many subdomains you want to search for\n'
                                    '[syntax: 100 or 1000 or 10000]' +
                f"{Colors.RED}" + ' ["p" to return]' + Colors.END +'\n')
            enteredNumber = input(f"{Colors.GREEN}")
            if bool(re.match('^(100|1000|10000)$', enteredNumber)):
                print('Subdomain list with ' + enteredNumber + ' possible subdomains will be used')
                self.subdomain_file = enteredNumber
                self.importer.change_subdomain_file(self.subdomain_file)
                self.go_to_menu(3, IMPORTER_MENU, self.import_menue_def)
            elif enteredNumber == 'p':
                self.go_to_menu(0, IMPORTER_MENU, self.import_menue_def)
            else:
                print(f"{Colors.RED}" + 'Error: invalid input.' + Colors.END)
                time.sleep(1)
                self.import_menue_def('3')
        else:
            print(f"{Colors.RED}" + 'The user input was invalid, please only use allowed characters.' + Colors.END)
            x = input()
            self.import_menue_def(x)

    def information_menu_def(self, user_input):
        self.status = 6

        entered_domain = ''

        if user_input == 'p':
            self.status = 0
            self.clear()
            self.start()
        elif user_input == '1':
            self.clear()
            print('Enter the domain for which you want to add a comment.\n'
                                    '[syntax: w-hs.de]' +
                ' ["p" to return]' + Colors.END +'\n')
            entered_domain = input(f"{Colors.GREEN}")
            if bool(re.match('.{2,40}\.\w{2,3}', entered_domain)):
                self.clear()
                print(f"{entered_domain} has been chosen")
                print('Enter the comment you want to add to the domain\n' +
                    f"{Colors.RED}" + ' ["p" to return]' + Colors.END +'\n')
                comment = input(f"{Colors.GREEN}")
                if comment == 'p':
                    self.go_to_menu(0, INDORMATION_MENU, self.information_menu_def)
                else:
                    self.add_comment_to_domain(entered_domain, comment)
                    print(f"{entered_domain} now has the comment = {comment}")
                    self.go_to_menu(3, INDORMATION_MENU, self.information_menu_def)
            else:
                print(f"{Colors.RED}" + 'The user input was invalid, please only use allowed characters.' + Colors.END)
                x = input(f"{Colors.GREEN}")
                self.information_menu_def(x)
        elif user_input == '2':
            self.clear()
            print('Enter the FQDN of the domainquery for which you want to add a comment.\n'
                                    '[syntax: w-hs.de]' +
                ' ["p" to return]' + Colors.END +'\n')
            entered_domain = input(f"{Colors.GREEN}")
            if bool(re.match('.{2,40}\.\w{2,3}', entered_domain)):
                self.clear()
                print(f"{entered_domain} has been chosen")
                print('Enter the date of the domainquery for which you want to add a comment\n'
                                    '[syntax: YYYY-MM-DD HH:MM:SS]' +
                ' ["p" to return]' + Colors.END +'\n')
                entered_date = input(f"{Colors.GREEN}")
                if bool(re.match('^([0-9]{4})-([0-1][0-9])-([0-3][0-9])\s([0-1][0-9]|[2][0-3]):([0-5][0-9]):([0-5][0-9])$', entered_date)):
                    print('Write comment you want to add to the domain\n' +
                        f"{Colors.RED}" + ' ["p" to return]' + Colors.END +'\n')
                    comment = input(f"{Colors.GREEN}")
                    if comment == 'p':
                        self.go_to_menu(0, INDORMATION_MENU, self.information_menu_def)
                    else:
                        self.add_comment_to_domainquery(entered_domain, comment, entered_date)
                        print(f"{entered_domain} now has the comment = {comment}")
                        self.go_to_menu(3, INDORMATION_MENU, self.information_menu_def)
                else:
                    print(f"{Colors.RED}" + 'The user input was invalid, please only use allowed characters.' + Colors.END)
                    x = input(f"{Colors.GREEN}")
                    self.information_menu_def(x)
            else:
                print(f"{Colors.RED}" + 'The user input was invalid, please only use allowed characters.' + Colors.END)
                x = input(f"{Colors.GREEN}")
                self.information_menu_def(x)
        elif user_input == '3':
            self.clear()
            print('Enter the FQDN of the domainquery for which you want to add a category\n'
                                    '[syntax: w-hs.de]' +
                ' ["p" to return]' + Colors.END +'\n')
            entered_domain = input(f"{Colors.GREEN}")
            if bool(re.match('.{2,40}\.\w{2,3}', entered_domain)):
                self.clear()
                print(f"{entered_domain} has been chosen")
                print('Enter the date of the domainquery for which you want to add a category\n'
                                    '[syntax: YYYY-MM-DD HH:MM:SS]' +
                ' ["p" to return]' + Colors.END +'\n')
                entered_date = input(f"{Colors.GREEN}")
                if bool(re.match('^([0-9]{4})-([0-1][0-9])-([0-3][0-9])\s([0-1][0-9]|[2][0-3]):([0-5][0-9]):([0-5][0-9])$', entered_date)):
                    print('Enter the category you want to add to the domain\n' +
                        f"{Colors.RED}" + ' ["p" to return]' + Colors.END +'\n')
                    category = input(f"{Colors.GREEN}")
                    if bool(re.match('[1-9]', category)):
                        self.add_category_to_domainquery(entered_domain, category, entered_date)
                        print(f"{entered_domain} has now the category = {category}")
                        self.go_to_menu(3, INDORMATION_MENU, self.information_menu_def)
                    elif category == 'p':
                        self.go_to_menu(0, INDORMATION_MENU, self.information_menu_def)
                    else:
                        print(f"{Colors.RED}" + 'The user input was invalid, please only use allowed characters.' + Colors.END)
                        x = input()
                        self.information_menu_def(x)
                else:
                    print(f"{Colors.RED}" + 'The user input was invalid, please only use allowed characters.' + Colors.END)
                    x = input()
                    self.information_menu_def(x)
        else:
            print(f"{Colors.RED}" + 'The user input was invalid, please only use allowed characters.' + Colors.END)
            x = input()
            self.information_menu_def(x)

    def status_menu_def(self, user_input):

        if user_input == 'p':
            self.updates_status = False
            self.worker.join()
            self.status = 0
            self.clear()
            self.start()
        else:
            print(f"{Colors.RED}" + 'The user input was invalid, please only use allowed characters.' + Colors.END)
            x = input()
            self.status_menu_def(x)

    def handle_input(self, user_input):

        if self.status == 0:
            if user_input == '1':
                self.go_to_menu(0, QUERY_MENU, self.query_menu_def)
            elif user_input == '2':
                self.go_to_menu(0, SCHEDULER_MENU, self.scheduler_menu_def)
            elif user_input == '3':
                self.go_to_menu(0, REPORTING_MENU, self.reporting_menu_def)
            elif user_input == '4':
                self.go_to_menu(0, IMPORTER_MENU, self.import_menue_def)
            elif user_input == '5':
                self.worker = threading.Thread(target=self.update_status)
                self.worker.daemon = True
                self.updates_status = True
                self.worker.start()
                self.go_to_menu(0, '', self.status_menu_def)
            elif user_input == '6':
                self.go_to_menu(0, INDORMATION_MENU, self.information_menu_def)
            elif user_input == 'x':
                self.clear()
                self.exit_programm()
            elif user_input == 'p':
                print(f"{Colors.RED}" + 'No previous menu existing, to exit enter "x".' + Colors.END)
                x = input()
                self.handle_input(x)
            else:
                print(f"{Colors.RED}" + 'The user input was invalid, please only use allowed characters.' + Colors.END)
                x = input()
                self.handle_input(x)


    def start(self):
        self.clear()
        print(f"{Colors.RED}" + LOGO + Colors.END + '\n' + MAIN_MENU)
        x = input()
        self.handle_input(x)

    def exit_programm(self):
        for key in self.processes:
            self.processes[key].terminate()
        exit()

    def go_to_menu(self, sleep_time, previous_menu_name, previous_menu_function):
        time.sleep(sleep_time)
        self.clear()
        print(f"{Colors.RED}" + LOGO + Colors.END + '\n' + previous_menu_name)
        previous_menu_function(input())

    def start_process(self, process_name, function):
        p = multiprocessing.Process(target = function)
        p.start()
        self.processes[process_name] = p

    def stop_process(self, process_name):
        self.processes[process_name].terminate()

    def restart_process(self, process_name, function):
        self.stop_process(process_name)
        self.start_process(process_name, function)
