#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
HTW-PV3 - Main file

Export weatherdata for PVSOL and POLYSUN
Run pvlib modell

SPDX-License-Identifier: AGPL-3.0-or-later
"""

__copyright__ = "© Ludwig Hülk"
__license__ = "GNU Affero General Public License Version 3 (AGPL-3.0)"
__url__ = "https://www.gnu.org/licenses/agpl-3.0.en.html"
__author__ = "Ludee;"
__version__ = "v0.0.2"

from settings import setup_logger, postgres_session, read_from_csv
from pv3_export_polysun import export_htw_polysun, export_fred_polysun
from pv3_export_pvsol import export_htw_pvsol, export_fred_pvsol
from pv3_sonnja_pvlib import setup_pvlib_location_object, setup_modelchain, run_modelchain, setup_htw_pvsystem_wr3, \
    setup_htw_pvsystem_wr4, setup_htw_pvsystem_wr2

import pandas as pd
from sqlalchemy import *

import time


DATA_VERSION = 'htw_pv3_v0.0.1'

if __name__ == "__main__":

    """logging"""
    log = setup_logger()
    start_time = time.time()
    log.info(f'PV3 model started with data version: {DATA_VERSION}')

    """database"""
    con = postgres_session()

    """Read data"""
    # read htw weatherdata from file
    # fn_htw = r'.\data\pv3_2015\pv3_weather_2015_filled_mview.csv'
    # df_htw_file = read_from_csv(fn_htw)

    # fn_fred = r'.\data\pv3_2015\openfred_weatherdata_2015_htw.csv'
    # df_fred_file = read_from_csv(fn_fred)

    # read htw weatherdata from sonnja_db
    sql = text("""
        SELECT  *                                  -- column
        FROM    pv3.pv3_weather_2015_filled_mview  -- table
        """)
    df_htw = pd.read_sql_query(sql, con)
    df_htw = df_htw.set_index('timestamp')

    # read open_FRED weatherdata from sonnja_db
    sql = text("""
        SELECT  *                                  -- column
        FROM    pv3.openfred_weatherdata_2015_htw  -- table
        """)
    df_fred = pd.read_sql_query(sql, con)
    df_fred = df_fred.set_index('timestamp')

    # """Export data"""
    # # Export HTW for POLYSUN
    # fn_polysun = 'pv3_htw_polysun_1min_2015.csv'
    # export_htw_polysun(df_htw, fn_polysun, 'M', 'g_hor_si')
    #
    # file_name_polysun_1h = 'pv3_htw_polysun_1h_2015.csv'
    # df_db_htw_weather_1h = df_htw.resample('1H').mean()
    # export_htw_polysun(df_db_htw_weather_1h, file_name_polysun_1h, 'H', 'g_hor_si')
    #
    # # Export HTW for PVSOL
    # file_name_pvsol_1h = 'pv3_htw_pvsol_1h_2015.dat'
    # df_db_htw_weather_1h = df_htw.resample('1H').mean()
    # export_htw_pvsol(df_db_htw_weather_1h, file_name_pvsol_1h)
    #
    # # Export FRED for POLYSUN
    # fn_fred_polysun = 'pv3_fred_polysun_1h_2015.csv'
    # export_fred_polysun(df_fred, fn_fred_polysun, 'H')
    #
    # # Export FRED for PVSOL
    # fn_fred_pvsol = 'pv3_fred_pvsol_1h_2015.dat'
    # export_fred_pvsol(df_fred, fn_fred_pvsol)


    # Run pvlib model

    # location
    htw_location = setup_pvlib_location_object()

    # pv system
    wr2 = setup_htw_pvsystem_wr2()
    wr3 = setup_htw_pvsystem_wr3()
    print(wr3)
    wr4 = setup_htw_pvsystem_wr4()
    # weather data
    df_fred_pvlib = df_fred.resample('H').mean()

    # model chains
    mc2 = setup_modelchain(wr2, htw_location)
    mc3 = setup_modelchain(wr3, htw_location)
    mc4 = setup_modelchain(wr4, htw_location)

    run_modelchain(mc2, df_fred_pvlib)
    run_modelchain(mc3, df_fred_pvlib)
    #run_modelchain(mc3, df_htw) # Add DHI
    run_modelchain(mc4, df_fred_pvlib)

    print(mc3.aoi)
    print(mc3.dc)
    print(mc3.ac)

    """close"""
    log.info('PV3 weather converter script successfully executed in {:.2f} seconds'
             .format(time.time() - start_time))
