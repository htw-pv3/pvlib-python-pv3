#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
HTW-PV3 - Export weather data for PVSOL

Export weatherdata for PVSOL

SPDX-License-Identifier: AGPL-3.0-or-later
"""

__copyright__ = "© Ludwig Hülk"
__license__ = "GNU Affero General Public License Version 3 (AGPL-3.0)"
__url__ = "https://www.gnu.org/licenses/agpl-3.0.en.html"
__author__ = "Ludee;"
__version__ = "v0.0.2"

import pandas as pd

from settings import HTW_LAT, HTW_LON
from pv3_weatherdata import calculate_diffuse_irradiation
from settings import write_to_csv

import logging
log = logging.getLogger(__name__)


def export_htw_pvsol(df_weather, filename):
    """TODO: Docu"""

    ## 1. Die erste Zeile enthält den Namen des Standorts.
    pvsol_first_row = 'PV3 - HTW Wetter - g_hor_si Stundenmittelwerte 2015\n'

    ## 2. Die zweite Zeile enthält Breitengrad, Längengrad, Höhe über NN, Zeitzone und ein Flag.
    pvsol_second_row = f'{HTW_LAT:.4f},-{HTW_LON:.4f},81,-1,-30\n'

    ## 3. Die dritte Zeile bleibt leer
    pvsol_third_row = '\n'

    ## 4. Vierte Zeile: Kopfzeile für Messwerte, mit 4 Spalten:
    # Ta - Umgebungstemperatur in °C
    # Gh - Globalstrahlung horizontal in Wh/m²
    # FF - Windgeschwindigkeit in m/s
    # RH - relative Luftfeuchtigkeit in %
    pvsol_fourth_row = 'Ta\tGh\tFF\tRH\n'

    with open(f'./data/{filename}', "w") as text_file:
        text_file.write(
            pvsol_first_row + pvsol_second_row + pvsol_third_row + pvsol_fourth_row)

    # rename columns
    PRINT_NAMES = {'g_hor_si': 'Gh [W/m²]',
                   't_luft': 'Ta [°C]',
                   'v_wind': 'FF [m/s]',
                   'h_luft': 'RH [%]'
                   }

    df_pvsol = df_weather.loc[:, ['t_luft', 'g_hor_si',  'v_wind', 'h_luft']].reset_index(drop=True)
    df_pvsol = df_pvsol.rename(columns=PRINT_NAMES)
    df_pvsol = df_pvsol.round(1)

    write_to_csv(f'./data/{filename}', df_pvsol,
                 index=False, sep='\t')

    log.info(f'Write data to file: {filename}')


def export_fred_pvsol(df, filename):
    """TODO: Docu"""

    # resample
    df = df.resample('H').mean()
    # 1 additional hour found, reduce to 8760 h
    df = df.loc['2015-01-01 00:00':'2015-12-31 23:00']

    df['h_luft'] = 0

    column_names = {"ghi": "g_hor_si",
                    "wind_speed": 'v_wind',
                    "temp_air": 't_luft',
                    }

    df = df.rename(columns=column_names)

    fred_lat = df['lat'][0]
    fred_lon = df['lon'][0]

    ## 1. Die erste Zeile enthält den Namen des Standorts.
    pvsol_first_row = 'PV3 - Open_FRED - Stundenmittelwerte 2015\n'

    ## 2. Die zweite Zeile enthält Breitengrad, Längengrad, Höhe über NN, Zeitzone und ein Flag.
    # Todo altitude/Zeitzone?
    pvsol_second_row = f'{fred_lat:.4f},-{fred_lon:.4f},81,-1,-30\n'

    ## 3. Die dritte Zeile bleibt leer
    pvsol_third_row = '\n'

    ## 4. Vierte Zeile: Kopfzeile für Messwerte, mit 4 Spalten:
    # Ta - Umgebungstemperatur in °C
    # Gh - Globalstrahlung horizontal in Wh/m²
    # FF - Windgeschwindigkeit in m/s
    # RH - relative Luftfeuchtigkeit in %
    pvsol_fourth_row = 'Ta\tGh\tFF\tRH\n'

    with open(f'./data/{filename}', "w") as text_file:
        text_file.write(pvsol_first_row + pvsol_second_row + pvsol_third_row + pvsol_fourth_row)

    write_to_csv(f'./data/{filename}', df, index=False, sep='\t')

    log.info(f'Write data to file: {filename}')
