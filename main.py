#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
HTW-PV3


SPDX-License-Identifier: AGPL-3.0-or-later
"""

__copyright__ = "© Ludwig Hülk"
__license__ = "GNU Affero General Public License Version 3 (AGPL-3.0)"
__url__ = "https://www.gnu.org/licenses/agpl-3.0.en.html"
__author__ = "Ludee;"
__version__ = "v0.0.1"

from config import setup_logger
import time

DATA_VERSION = 'htw_pv3_v0.0.1'

if __name__ == "__main__":
    log = setup_logger()
    start_time = time.time()
    log.info(f'PV3 script started with data version: {DATA_VERSION}')

    