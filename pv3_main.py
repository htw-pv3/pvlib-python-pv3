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

from settings import setup_logger
from settings import postgres_session
from settings import write_to_csv
from pv3_weatherdata import setup_weather_dataframe,calculate_diffuse_irradiation,\
    read_weatherdata, create_polysun, create_pvsol, convert_open_FRED
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

    #################
    """HTW-weatherdata"""
    #################

    file_name_htw = r'.\data\pv3_2015\htw_wetter_weatherdata_2015.csv'
    
    # read weatherdata
    df_w = read_weatherdata(file_name_htw)

    sql = text("""
        SELECT  timestamp, g_gen_cmp11, g_gen_si   -- column
        FROM    pv3.pv3_weather_2015_filled_mview  -- table
        """)
    df_db_htw_weather = pd.read_sql_query(sql, con)
    df_db_htw_weather = df_db_htw_weather.set_index('timestamp')
    print(df_db_htw_weather.head(10))

    # HTW coords
    lat = 52.455778
    lon = 13.523917

    # calc diffuse irradiation
    parameter_name = 'G_hor_Si'   # GHI
    htw_weather_data_dhi_dni = calculate_diffuse_irradiation(df_w, parameter_name, lat, lon)

    #################
    # Export for Polysun

    df_polysun = create_polysun(df_w, htw_weather_data_dhi_dni)

    write_to_csv('./data/htw_pv3_polysun_2015.csv', df_polysun, append=False, index=False)

    ## 1. Todo Doku
    polysun_first_row = '# Station: HTW Berlin, PVlib\n'
    ## 2. Todo Doku
    polysun_second_row = f'# Latitude: {lat:.4f} Longitude: {lon:.4f} altitude: 81m\n'
    ## 3. Todo Doku
    polysun_third_row = '#'
    with open("./data/htw_pv3_polysun_2015.csv", "r+") as text_file:
        content = text_file.read()
        text_file.seek(0, 0)
        text_file.write(polysun_first_row+polysun_second_row+polysun_third_row + '\n' + content)

    #################
    # Export for PVSol

    ## 1. Die erste Zeile enthält den Namen des Standorts.
    pvsol_first_row = 'Htw Wetter G_hor_si Stundenmittelwerte 2015\n'

    ## 2. Die zweite Zeile enthält Breitengrad, Längengrad, Höhe über NN, Zeitzone und ein Flag.
    pvsol_second_row = f'{lat:.4f},-{lon:.4f},81,-1,-30\n'

    ## 3. Die dritte Zeile bleibt leer
    pvsol_third_row = '\n'

    ## 4. Vierte Zeile: Kopfzeile für Messwerte, mit 4 Spalten:
    # Ta - Umgebungstemperatur in °C
    # Gh - Globalstrahlung horizontal in Wh/m²
    # FF - Windgeschwindigkeit in m/s
    # RH - relative Luftfeuchtigkeit in %
    pvsol_fourth_row = 'Ta\tGh\tFF\tRH\n'

    with open("./data/htw_pv3_pvsol_2015.dat", "w") as text_file:
        text_file.write(pvsol_first_row+pvsol_second_row+pvsol_third_row+pvsol_fourth_row)

    htw_weather_data_pvsol = create_pvsol(df_w)
    write_to_csv('./data/htw_pv3_pvsol_2015.dat', htw_weather_data_pvsol, index=False, sep='\t')



    #################
    """open_FRED - weatherdata"""
    #################


    file_name_fred = r'.\data\pv3_2015\openfred_weatherdata_2015_htw.csv'
    
    df_w, lat, lon = convert_open_FRED(file_name_fred)

    #################
    # Export for Polysun

    # dhi doesnt have to be calculated as it is already inegrated
    df_polysun = create_polysun(df_w, df_w)
    write_to_csv('./data/FRED_pv3_polysun_2015.csv', df_polysun, append=False, index=False)

    ## 1. Todo Doku
    polysun_first_row = '# Open_FRED Wetter Stundenmittelwerte 2015\n'
    ## 2. Todo Doku
        # Todo altitude
    polysun_second_row = f'# Latitude: {lat:.4f} Longitude: {lon:.4f} altitude: 81m\n'
    ## 3. Todo Doku
    polysun_third_row = '#'
    with open("./data/FRED_pv3_polysun_2015.csv", "r+") as text_file:
        content = text_file.read()
        text_file.seek(0, 0)
        text_file.write(polysun_first_row + polysun_second_row + polysun_third_row + '\n' + content)


    #################
    # Export for PVSol

    ## 1. Die erste Zeile enthält den Namen des Standorts.
    pvsol_first_row = 'Open_FRED Wetter Stundenmittelwerte 2015\n'

    ## 2. Die zweite Zeile enthält Breitengrad, Längengrad, Höhe über NN, Zeitzone und ein Flag.
    # Todo altitude/Zeitsone?
    pvsol_second_row = f'{lat:.4f},-{lon:.4f},81,-1,-30\n'

    ## 3. Die dritte Zeile bleibt leer
    pvsol_third_row = '\n'

    ## 4. Vierte Zeile: Kopfzeile für Messwerte, mit 4 Spalten:
    # Ta - Umgebungstemperatur in °C
    # Gh - Globalstrahlung horizontal in Wh/m²
    # FF - Windgeschwindigkeit in m/s
    # RH - relative Luftfeuchtigkeit in %
    pvsol_fourth_row = 'Ta\tGh\tFF\tRH\n'

    with open("./data/FRED_pv3_pvsol_2015.dat", "w") as text_file:
        text_file.write(pvsol_first_row + pvsol_second_row + pvsol_third_row + pvsol_fourth_row)

    htw_weather_data_pvsol = create_pvsol(df_w)
    write_to_csv('./data/FRED_pv3_pvsol_2015.dat', htw_weather_data_pvsol, index=False, sep='\t')




    """close"""
    log.info('PV3 weather converter script successfully executed in {:.2f} seconds'
             .format(time.time() - start_time))
