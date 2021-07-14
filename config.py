#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
HTW-PV3 - Config file functions (not used atm)

Create and handle a config file for database connection

SPDX-License-Identifier: AGPL-3.0-or-later
"""

__copyright__ = "© Ludwig Hülk"
__license__ = "GNU Affero General Public License Version 3 (AGPL-3.0)"
__url__ = "https://www.gnu.org/licenses/agpl-3.0.en.html"
__author__ = "Ludee;"
__version__ = "v0.0.2"

import os
import configparser as cp

"""parameter"""
cfg = cp.RawConfigParser()
config_file = 'config.ini'

# Datenbankzugriffe, Host, Port, User, Passwort, ...
def config_section_set(config_section, host, port, user, pw):
    """Create a config file.

    Sets input values to a [db_section] key - pair.

    Parameters
    ----------
    config_section : str
        Section in config file = database_name.
    host : str
        The database host = localhost.
    port : str
        The database port.
    user : str
        The database user.
    pw : str
        The PW.
    """

    with open(config_file, 'w') as config:  # save
        if not cfg.has_section(config_section):
            cfg.add_section(config_section)
            cfg.set(config_section, 'host', host)
            cfg.set(config_section, 'port', port)
            cfg.set(config_section, 'user', user)
            cfg.set(config_section, 'pw', pw)
            cfg.write(config)

# Einlesen der Datenbankzugriffe
def config_file_load():
    """Load the username and pw from config file."""

    if os.path.isfile(config_file):
        config_file_init()
    else:
        config_file_not_found_message()

# Initialisieren und checken der Datenbankzugriffe
def config_file_init():
    """Read config file."""

    try:
        # print('Load ' + config_file)
        cfg.read(config_file)
        global _loaded
        _loaded = True
    except FileNotFoundError:
        config_file_not_found_message()

# Setting auslesen
def config_file_get(config_section, port):
    """Read data from config file.

    Parameters
    ----------
    config_section : str
        Section in config file.
    port : str
        Config entries.
    """

    if not _loaded:
        config_file_init()
    try:
        return cfg.getfloat(config_section, port)
    except Exception:
        try:
            return cfg.getint(config_section, port)
        except:
            try:
                return cfg.getboolean(config_section, port)
            except:
                return cfg.get(config_section, port)

# Ausagebemessage, wenn file nicht gefunden wurde
def config_file_not_found_message():
    """Show error message if file not found."""

    print(f'The config file "{config_file}" could not be found')

# Erstellen der Postgres-Session(gleiche Funktion, wie bei Juypter Notebook)
def setup_config():
    """Access config.ini.

    Returns
    -------
    user : str
        marktakteurMastrNummer (value).
    token : str
        API token (key).
    """
    config_section = 'MaStR'

    # user
    try:
        config_file_load()
        user = config_file_get(config_section, 'user')
        # print('Hello ' + user)
    except:
        user = input('Please provide your MaStR Nummer:')

    # token
    try:
        from settings import config_file_get
        token = config_file_get(config_section, 'token')
    except:
        import sys
        token = input('Token:')
        # token = getpass.getpass(prompt='apiKey: ',
        #                            stream=sys.stderr)
        config_section_set(config_section, value=user, key=token)
        print('Config file created.')
    return user, token
