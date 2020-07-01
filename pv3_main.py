#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
HTW-PV3


SPDX-License-Identifier: AGPL-3.0-or-later
"""

__copyright__ = "© Ludwig Hülk"
__license__ = "GNU Affero General Public License Version 3 (AGPL-3.0)"
__url__ = "https://www.gnu.org/licenses/agpl-3.0.en.html"
__author__ = "Ludee;"
__version__ = "v0.0.1"

from config import setup_logger
from config import postgres_session
from pv3_weatherdata import setup_weather_dataframe

import time


DATA_VERSION = 'htw_pv3_v0.0.1'

if __name__ == "__main__":

    """logging"""
    log = setup_logger()
    start_time = time.time()
    log.info(f'PV3 script started with data version: {DATA_VERSION}')

    """database connection"""
    # con = postgres_session()

    """weatherdata"""
    htw_weather_data = setup_weather_dataframe(weather_data='open_FRED')
    htw_weather_data.head()

    """close"""
    log.info('MaSTR script successfully executed in {:.2f} seconds'
             .format(time.time() - start_time))