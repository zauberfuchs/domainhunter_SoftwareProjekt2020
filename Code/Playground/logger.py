import logging
from logging.handlers import TimedRotatingFileHandler

# Dieser Logger erstellt jeden Tag um 0:00 Uhr eine neue Log Datei
# To-Do: Einfügen in Klasse Scheduler und sinnvolle Logs formulieren

formatter = logging.Formatter('%(asctime)s:%(levelname)s: %(message)s')

handler = TimedRotatingFileHandler('domainhunter.log', when="midnight", interval=1)
handler.setFormatter(formatter)
handler.suffix = "%Y%m%d"

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)      # Mit DEBUG Einstellung werden alle logs sämtlicher Kategorien angezezeigt
logger.addHandler(handler)

# Log Beispiele:
logging.debug('Detailed information, typically of interest only when diagnosing problems.')

logging.info('Confirmation that things are working as expected')

logging.warning('An indication that something unexpected happened, or indicative of some problem in the near '
                'future (e.g. “disk space low”). The software is still working as expected')

logging.error('Due to a more serious problem, the software has not been able to perform some function.')

logging.critical('A serious error, indicating that the program itself may be unable to continue running.')