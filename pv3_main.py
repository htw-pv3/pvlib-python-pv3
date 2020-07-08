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
from pv3_weatherdata import setup_weather_dataframe, calculate_diffuse_irradiation, read_weatherdata, create_polysun
import pandas as pd

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
    # write_to_csv('./data/htw_weather_data_dhi_dni.csv', htw_weather_data_dhi_dni)


    # Export for Polysun
    df_polysun = create_polysun(df_w, htw_weather_data_dhi_dni)
    write_to_csv('./data/htw_pv3_polysun_2015.csv', df_polysun, index=False)

    ## 1. Todo Doku
    polysun_first_row = '# Station: HTW Berlin, PVlib\n'
    ## 2. Todo Doku
    polysun_second_row = '# Latitude: 52.4557 Longitude: -13.5239 altitude: 81m\n'
    ## 3. Todo Doku
    polysun_third_row = '#'
    with open("./data/htw_pv3_polysun_2015.csv", "r+") as text_file:
        content = text_file.read()
        text_file.seek(0, 0)
        text_file.write(polysun_first_row+polysun_second_row+polysun_third_row + '\n' + content)


    # Export for PVSol

    ## 1. Die erste Zeile enthält den Namen des Standorts.
    pvsol_first_row = 'Htw Wetter G_hor_si Stundenmittelwerte'

    ## 2. Die zweite Zeile enthält Breitengrad, Längengrad, Höhe über NN, Zeitzone und ein Flag.
    pvsol_second_row = '52.4557,-13.5239,81,-1,-30'

    ## 3. Die dritte Zeile bleibt leer
    pvsol_third_row = ''

    ## 4. Vierte Zeile: Kopfzeile für Messwerte, mit 4 Spalten:
    # Ta - Umgebungstemperatur in °C
    # Gh - Globalstrahlung horizontal in Wh/m²
    # FF - Windgeschwindigkeit in m/s
    # RH - relative Luftfeuchtigkeit in %

    #pvsol_header = pd.DataFrame([x.split(';') for x in pvsol_third_row.split('\n')])
    #write_to_csv('./data/htw_pv3_pvsol_2015.dat', pvsol_header)

    """close"""
    log.info('MaSTR script successfully executed in {:.2f} seconds'
             .format(time.time() - start_time))
