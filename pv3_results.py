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

from settings import setup_logger

"""logging"""
log = setup_logger()


def results_modelchain_annual_yield(mc):

    mc_ac = mc.ac
    annual_yield = round(mc_ac.sum() / 1000, 3)
    system_name = mc.system.name

    log.info(f'Annual yield for {system_name}: {annual_yield}')

    return mc_ac, annual_yield
