#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
HTW-PV3 Main file


SPDX-License-Identifier: AGPL-3.0-or-later
"""

__copyright__ = "© Ludwig Hülk"
__license__ = "GNU Affero General Public License Version 3 (AGPL-3.0)"
__url__ = "https://www.gnu.org/licenses/agpl-3.0.en.html"
__author__ = "Ludee;"
__version__ = "v0.0.1"

from config import setup_logger
from config import postgres_session, write_to_csv
from pv3_weatherdata import setup_weather_dataframe, calculate_diffuse_irradiation, read_weatherdata

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
    #htw_weather_data = setup_weather_dataframe(weather_data='open_FRED')
    #htw_weather_data.head()
    file_name = 'D:\git\github\htw-pv3\pvlib-python-pv3\data\pv3_2015\htw_wetter_weatherdata_2015.csv'
    df_w = read_weatherdata(file_name)

    # HTW coords
    lat = 52.455778
    lon = 13.523917
    parameter_name = 'G_hor_Si'   # GHI
    htw_weather_data_dhi_dni = calculate_diffuse_irradiation(df_w, parameter_name, lat, lon)
    htw_weather_data_dhi_dni.head()

    write_to_csv('./data/htw_weather_data_dhi_dni.csv', htw_weather_data_dhi_dni)


    """close"""
    log.info('MaSTR script successfully executed in {:.2f} seconds'
             .format(time.time() - start_time))
