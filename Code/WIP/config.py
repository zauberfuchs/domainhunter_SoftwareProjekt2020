#!/usr/bin/python
from configparser import ConfigParser


def config(filename='databasetest.ini', section='postgresql'):
    # erstellen eines Parsers
    parser = ConfigParser()
    # lesen der config Datei
    parser.read(filename)

    # Parsen und übergeben
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))

    return db
