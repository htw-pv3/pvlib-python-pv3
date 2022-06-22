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

from settings import setup_logger, postgres_session, query_database, read_from_csv, write_to_csv, HTW_LON, HTW_LAT
from pv3_sonnja_pvlib import setup_pvlib_location_object, setup_modelchain, run_modelchain, setup_htw_pvsystem_wr3, \
    setup_htw_pvsystem_wr4, setup_htw_pvsystem_wr2, setup_htw_pvsystem_wr1, setup_htw_pvsystem_wr5
from pv3_weatherdata import calculate_diffuse_irradiation
from pv3_results import results_modelchain_annual_yield, results_per_month

import pandas as pd
from sqlalchemy import *

import time


DATA_VERSION = 'htw_pv3_v0.0.1'

if __name__ == "__main__":

    """logging"""
    log = setup_logger()
    start_time = time.time()

    """database"""
    con = postgres_session()
    log.info(f'PV3 model started with data version: {DATA_VERSION}')

    """Read data"""

    # read htw weatherdata from file
    # fn_htw = r'.\data\pv3_2015\pv3_weather_2015_filled_mview.csv'
    # df_htw_file = read_from_csv(fn_htw)
    # fn_fred = r'.\data\pv3_2015\openfred_weatherdata_2015_htw.csv'
    # df_fred_file = read_from_csv(fn_fred, sep=',')

    # read htw weatherdata from sonnja_db
    schema = 'pv3'
    table = 'htw_weatherdata_2015'
    df_htw = query_database(con, schema, table)

    htw_weatherdata_names = {"g_hor_si": "ghi",
                             'v_wind': "wind_speed",
                             't_luft': "temp_air",
                             }
    df_htw = df_htw.rename(columns=htw_weatherdata_names)
    df_dhi = calculate_diffuse_irradiation(df_htw, "ghi", HTW_LAT, HTW_LON)
    df_htw = df_htw.merge(df_dhi[['dhi', 'dni']], left_index=True, right_index=True)
    df_htw_select = df_htw.loc[:, ["ghi", "dhi", 'dni', "wind_speed", "temp_air"]]
    df_htw_pvlib = df_htw_select.resample('H').mean()

    # read open_FRED weatherdata from sonnja_db
    schema = 'pv3'
    table = 'openfred_weatherdata_2015_htw'
    df_fred = query_database(con, schema, table)


    # Run pvlib model

    # location
    htw_location = setup_pvlib_location_object()

    # Set up pv systems
    wr1 = setup_htw_pvsystem_wr1()
    wr2 = setup_htw_pvsystem_wr2()
    wr3 = setup_htw_pvsystem_wr3()
    wr4 = setup_htw_pvsystem_wr4()
    wr5 = setup_htw_pvsystem_wr5()


    # weather data
    df_fred_pvlib = df_fred.resample('H').mean()

    # Set up list of pv systems
    pv_systems = [wr1,wr2,wr3,wr4,wr5]
    filenames = ["pv3_pvlib_mc1","pv3_pvlib_mc2","pv3_pvlib_mc3","pv3_pvlib_mc4","pv3_pvlib_mc5"]

    # Initialize list for mcs and mcs_htw
    results_fred_annual_wr = []
    results_htw_annual_wr = []

    # For loop iterates over all pv systems and saves results in csv files according to filenames
    for idx, system in enumerate(pv_systems):
        # setup Modelchain
        mc_fred = setup_modelchain(system,htw_location)
        mc_htw = setup_modelchain(system,htw_location)

        # run Modelchain
        run_modelchain(mc_fred, df_fred_pvlib)
        run_modelchain(mc_htw, df_htw_pvlib)

        # Calculate annual and monthly yield of Modelchain (PV System)

            # output1: raw wr yield ; output2: annual wr yield
        log.info(f'Yield from OpenFRED Weather Data')
        mc_ac_fred, res_ac_sum_fred = results_modelchain_annual_yield(mc_fred) 
        res_ac_month_fred = results_per_month(mc_ac_fred)
        
        log.info(f'Yield from HTW Weather Data')
        mc_ac_htw, res_ac_sum_htw = results_modelchain_annual_yield(mc_htw)
        res_ac_month_htw = results_per_month(mc_ac_htw)

        # Write data to csv files
        write_to_csv(f'./data/{filenames[idx]}_fred.csv', mc_ac_fred)
        write_to_csv(f'./data/{filenames[idx]}_fred_month.csv', res_ac_month_fred)        
        write_to_csv(f'./data/{filenames[idx]}_htw.csv', mc_ac_htw)
        write_to_csv(f'./data/{filenames[idx]}_htw_month.csv', res_ac_month_htw)

        #Save all mcs and mcs_htw in list
        results_fred_annual_wr.append(res_ac_sum_fred)
        results_htw_annual_wr.append(res_ac_sum_htw)

    # Printout Statements fred
    log.info(f'OpenFRED Weather Data')

    for idx, fred_yield in enumerate(results_fred_annual_wr,start=1):
        log.info(f'Annual yield WR{idx}: {fred_yield}')

    log.info(f'Annual yield SonnJA: {sum(results_fred_annual_wr)}')

    # Printout Statements HTW
    log.info(f'HTW Weather Data')

    for idx, htw_yield in enumerate(results_htw_annual_wr,start=1):
        log.info(f'Annual yield WR{idx}: {htw_yield}')

    log.info(f'Annual yield SonnJA: {sum(results_htw_annual_wr)}')

    """close"""
    log.info('PV3 SonnJA pvlib model successfully executed in {:.2f} seconds'
             .format(time.time() - start_time))
