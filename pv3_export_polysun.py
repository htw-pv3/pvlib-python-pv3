#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
HTW-PV3 - Export weather data for POLYSUN

Export weatherdata for POLYSUN

SPDX-License-Identifier: AGPL-3.0-or-later
"""

__copyright__ = "© Ludwig Hülk"
__license__ = "GNU Affero General Public License Version 3 (AGPL-3.0)"
__url__ = "https://www.gnu.org/licenses/agpl-3.0.en.html"
__author__ = "Ludee;"
__version__ = "v0.0.2"

import pandas as pd

from pv3_weatherdata import calculate_diffuse_irradiation
from settings import HTW_LAT, HTW_LON
from settings import write_to_csv

import logging
log = logging.getLogger(__name__)


def export_htw_polysun(df_weather, filename, resolution, parameter_name):
    """TODO: Docu"""

    # calc diffuse irradiation
    df_dhi = calculate_diffuse_irradiation(df_weather, parameter_name, HTW_LAT, HTW_LON)

    if resolution == 'M':
        s = 60
        steps = 525600
    elif resolution == 'H':
        s = 3600
        steps = 8760

    time = list(zip(range(steps), [s * i for i in range(steps)]))
    polysun = {}
    polysun = {'# Time [s]': dict(time)}

    polysun.update(
        df_weather.loc[:,
        ['g_hor_si', 't_luft', 'v_wind', 'h_luft']].reset_index(
            drop=True).to_dict())

    df_polysun = pd.DataFrame.from_dict(polysun)
    df_polysun = df_polysun.merge(df_dhi['dhi'].reset_index(drop=True),
                                  left_index=True, right_index=True)

    # zero values as not needed
    df_polysun['Lh [W/m²]'] = 0                 # Lh Langwellenstrahlung[Wh / m2]

    # rename columns
    PRINT_NAMES = {'g_hor_si': 'Gh [W/m²]',     # Gh Globalstrahlung [Wh/m2]
                   'dhi': 'Dh [W/m²]',          # Dh Diffusstrahlung [Wh/m2]
                   't_luft': 'Tamb [°C]',       # Tamb Umgebungstemperatur [°C]
                   'v_wind': 'Vwnd [m/s]',      # Vwnd Windgeschwindigkeit [m/s]
                   'h_luft': 'Hrel [%]',        # Hrel Luftfeuchtigkeit [%]
                   }
    df_polysun = df_polysun.rename(columns=PRINT_NAMES)

    df_polysun = df_polysun.loc[:,
                 ['# Time [s]', 'Gh [W/m²]', 'Dh [W/m²]', 'Tamb [°C]',
                  'Lh [W/m²]', 'Vwnd [m/s]', 'Hrel [%]']]

    df_polysun = df_polysun.round(1)

    write_to_csv(f'./data/{filename}', df_polysun, append=False,
                 index=False)

    ## 1. Todo Doku
    polysun_first_row = '# Station: HTW Berlin, PVlib\n'
    ## 2. Todo Doku
    polysun_second_row = f'# Latitude: {HTW_LAT:.4f} Longitude: {HTW_LON:.4f} altitude: 81m\n'
    ## 3. Todo Doku
    polysun_third_row = '#'
    with open(f'./data/{filename}', "r+") as text_file:
        content = text_file.read()
        text_file.seek(0, 0)
        text_file.write(
            polysun_first_row + polysun_second_row + polysun_third_row + '\n' + content)

    log.info(f'Write data to file: {filename}')


def export_fred_polysun(df, filename, resolution):
    """converts open_FRED data into HTW_Weatherdata format"""

    # dhi doesnt have to be calculated as it is already integrated

    # resample
    if resolution == 'M':
        s = 60
        steps = 525600
    elif resolution == 'H':
        s = 3600
        steps = 8760
        df = df.resample('H').mean()

        # 1 additional hour found, reduce to 8760 h
        df = df.loc['2015-01-01 00:00':'2015-12-31 23:00']


    df['h_luft'] = 0

    column_names = {"ghi": "g_hor_si",
                     "wind_speed": 'v_wind',
                     "temp_air": 't_luft',
                     }

    df_open_fred = df.rename(columns=column_names)

    fred_lat = df_open_fred['lat'][0]
    fred_lon = df_open_fred['lon'][0]

    time = list(zip(range(steps), [s * i for i in range(steps)]))
    polysun = {}
    polysun = {'# Time [s]': dict(time)}

    polysun.update(
        df_open_fred.loc[:,
        ['g_hor_si', 't_luft', 'v_wind', 'h_luft']].reset_index(
            drop=True).to_dict())

    df_polysun = pd.DataFrame.from_dict(polysun)

    write_to_csv(f'./data/{filename}', df_polysun, append=False, index=False)

    ## 1. Todo Doku
    polysun_first_row = '# Open_FRED Wetter Stundenmittelwerte 2015\n'
    ## 2. Todo Doku
        # Todo altitude
    polysun_second_row = f'# Latitude: {fred_lat:.4f} Longitude: {fred_lon:.4f} altitude: 81m\n'
    ## 3. Todo Doku
    polysun_third_row = '#'
    with open(f'./data/{filename}', "r+") as text_file:
        content = text_file.read()
        text_file.seek(0, 0)
        text_file.write(polysun_first_row + polysun_second_row + polysun_third_row + '\n' + content)

    log.info(f'Write data to file: {filename}')


# deprecated
def convert_open_FRED(file_name):
    """converts open_FRED data into HTW_Weatherdata format"""
    # read open_fred_weather_data
    htw_weatherdata_names = {"ghi": "g_hor_si",
                             "wind_speed": 'v_wind',
                             "temp_air": 't_luft',
                             }

    df_open_fred = pd.read_csv(file_name, index_col=0,
                               date_parser=pd.to_datetime)
    df_open_fred = df_open_fred.resample('H').mean()

    # 1 additional hour found, reduce to 8760 h
    df_open_fred = df_open_fred.loc['2015-01-01 00:00':'2015-12-31 23:00']

    df_open_fred['h_luft'] = 0

    df_open_fred = df_open_fred.rename(columns=htw_weatherdata_names)
    lat = df_open_fred['lat'][0]
    lon = df_open_fred['lon'][0]

    return df_open_fred, lat, lon
