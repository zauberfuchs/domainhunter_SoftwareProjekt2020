import logging
from logging.handlers import TimedRotatingFileHandler


# Logging initialisierung
formatter = logging.Formatter('%(asctime)s:%(levelname)s: %(message)s')

# Jeden Tag wird eine neue log Datei erstellt
handler_cli = TimedRotatingFileHandler('./Logs/cli.log', when="midnight", interval=1)
handler_cli.setFormatter(formatter)
handler_cli.suffix = "%Y%m%d"

handler_scheduler = TimedRotatingFileHandler('./Logs/scheduler.log', when="midnight", interval=1)
handler_scheduler.setFormatter(formatter)
handler_scheduler.suffix = "%Y%m%d"

logger_cli = logging.getLogger("cli")
logger_cli.setLevel(logging.DEBUG)
logger_cli.addHandler(handler_cli)

logger_scheduler = logging.getLogger("scheduler")
logger_scheduler.setLevel(logging.DEBUG)
logger_scheduler.addHandler(handler_scheduler)
