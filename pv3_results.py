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
__version__ = "v0.0.2"

from settings import setup_logger, write_to_csv

import pandas as pd

"""logging"""
log = setup_logger()


def results_modelchain(mc, weather):
    system_name = mc.system.name
    li_mc_ac = mc.ac
    li_mc_temp = mc.cell_temperature
    df_mc_dc = mc.dc
    df_mc_dc.index.name = 'timestamp'
    df_mc_weather = mc.weather
    df_mc_weather.index.name = 'timestamp'

    df = pd.DataFrame({'ac': li_mc_ac,
                       'cell_temperature': li_mc_temp,
                       })
    df.index.name = 'timestamp'

    df = df.merge(df_mc_dc, on='timestamp', how='right')
    df = df.merge(df_mc_weather, on='timestamp', how='right')

    filename = f'pv3_pvlib_{weather}_{system_name}'
    write_to_csv(f'./data/{filename}.csv', df, append=False)

    return df


def results_modelchain_per_month(mc, df, weather):
    system_name = mc.system.name
    df_month = df[['ac', 'p_mp']].resample('M').sum()
    df_month.insert(0, "weather", weather, True)
    df_month.insert(0, "system_name", system_name, True)

    write_to_csv(f'./data/pv3_pvlib_month.csv', df_month, append=True)

    return df_month


def results_modelchain_annual_yield(mc, weather):
    mc_ac = mc.ac
    system_name = mc.system.name

    annual_yield = round(mc_ac.sum() / 1000, 3)
    df = pd.DataFrame([[weather, system_name, annual_yield]],
                      columns=['weather', 'system', 'annual_yield'])
    df.set_index(["weather", 'system'], inplace=True)

    write_to_csv('./data/pv3_pvlib_annual.csv', df)

    log.info(f'Annual yield for {system_name}: {annual_yield}')

    return annual_yield
