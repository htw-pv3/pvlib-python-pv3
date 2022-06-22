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

    return df, filename


def results_modelchain_per_month(df, filename):
    df_month = df['ac'].resample('M').sum()
    # df_month = df_month['AC'].round(decimals=2)

    write_to_csv(f'./data/{filename}_month.csv', df_month, append=False)

    return df_month


def results_modelchain_annual_yield(mc, weather):
    mc_ac = mc.ac
    system_name = mc.system.name

    annual_yield = round(mc_ac.sum() / 1000, 3)
    df = pd.DataFrame([[weather, system_name, annual_yield]],
                      columns=['weather', 'system', 'annual_yield'])
    df.set_index(["weather", 'system'], inplace=True)

    filename = f'pv3_pvlib_{weather}_annual'
    write_to_csv(f'./data/{filename}.csv', df)

    log.info(f'Annual yield for {system_name}: {annual_yield}')

    return annual_yield
