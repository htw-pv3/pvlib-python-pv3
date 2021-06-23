
import sys
import getpass
from sqlalchemy import *


def postgres_session():
    """SQLAlchemy session object with valid connection to local database"""

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
