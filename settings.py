#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Service functions

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

import logging
log = logging.getLogger(__name__)

"""parameter"""
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


def postgres_session():
    """SQLAlchemy session object with valid connection to local database

    Returns
    -------
    con : connection
        SQLAlchemy connection object.

    TODO: Docstring + Use config.py
    """

    print('Please provide connection parameters to database:\n' +
          'Hit [Enter] to take defaults')
    host = 'localhost'  # input('host (default 127.0.0.1): ')
    port = '5432'  # input('port (default 5432): ')
    database = 'sonnja_db'  # input("database name (default 'sonnja_db'): ")
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
