#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Service functions for logging and database connection

Configure console and file logging;
Create and handle config file for database connection;

SPDX-License-Identifier: AGPL-3.0-or-later
"""

__copyright__ = "© Ludwig Hülk"
__license__ = "GNU Affero General Public License Version 3 (AGPL-3.0)"
__url__ = "https://www.gnu.org/licenses/agpl-3.0.en.html"
__author__ = "Ludee;"
__version__ = "v0.0.1"

import os
import sys
import getpass
from sqlalchemy import *
import configparser as cp
import logging
log = logging.getLogger(__name__)

"""parameter"""
cfg = cp.RawConfigParser()
config_file = 'config.ini'
log_file = 'pv3.log'


def setup_logger():
    """Configure logging in console and log file.

    Returns
    -------
    rl : logger
        Logging in console (ch) and file (fh).
    """

    rl = logging.getLogger()
    rl.setLevel(logging.INFO)
    rl.propagate = False

    # set format
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s',
                                  datefmt='%Y-%m-%d %H:%M:%S')

    # console handler (ch)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(formatter)

    # file handler (fh)
    fh = logging.FileHandler(log_file)
    fh.setLevel(logging.INFO)
    fh.setFormatter(formatter)

    rl.handlers = [ch, fh]

    return rl


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


def config_file_load():
    """Load the username and pw from config file."""

    if os.path.isfile(config_file):
        config_file_init()
    else:
        config_file_not_found_message()


def config_file_init():
    """Read config file."""

    try:
        # print('Load ' + config_file)
        cfg.read(config_file)
        global _loaded
        _loaded = True
    except FileNotFoundError:
        config_file_not_found_message()


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


def config_file_not_found_message():
    """Show error message if file not found."""

    print(f'The config file "{config_file}" could not be found')


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
        from config import config_file_get
        token = config_file_get(config_section, 'token')
    except:
        import sys
        token = input('Token:')
        # token = getpass.getpass(prompt='apiKey: ',
        #                            stream=sys.stderr)
        config_section_set(config_section, value=user, key=token)
        print('Config file created.')
    return user, token


def postgres_session():
    """SQLAlchemy session object with valid connection to local database"""

    print('Please provide connection parameters to database:')
    host = 'localhost'  # input('host (default 130.226.55.43): ')
    port = '5434'  # input('port (default 5432): ')
    database = 'sonnja_db'  # input("database name (default 'reeem'): ")
    user = 'sonnja'  # input('user (default postgres): ')
    password = input('password: ')
    #password = getpass.getpass(prompt='password: ',
    #                           stream=sys.stderr)

    con = create_engine(
        'postgresql://' + '%s:%s@%s:%s/%s' % (user,
                                              password,
                                              host,
                                              port,
                                              database)).connect()
    print('Password correct! Database connection established.')
    return con


def write_to_csv(csv_name, df, append=True, index=True, sep=';'):
    """Create CSV file or append data to it.

    Parameters
    ----------
    csv_name : str
        Name of file.
    df : DataFrame
        Sata saved to file.
    append : bool
        If False create a new CSV file (default), else append to it.
    index : bool
        If False do not write index into CSV file
    sep : str
        seperator to be used while writing csv. Semicolon ';' is standard
    """
    #if os.path.exists(os.path.dirname(csv_name)):
    #    os.remove(os.path.dirname(csv_name))

    if append:
        mode = 'a'
    else:
        mode = 'w'

    if not os.path.exists(os.path.dirname(csv_name)):
        os.makedirs(os.path.dirname(csv_name))

    with open(csv_name, mode=mode, encoding='utf-8') as file:
        df.to_csv(file, sep=sep,
                    mode=mode,
                    header=file.tell() == 0,
                    line_terminator='\n',
                    encoding='utf-8',
                    index=index
                 )

    log.info(f'Write data to file: {csv_name} with append-mode={append}')