#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PDX-License-Identifier: AGPL-3.0-or-later
"""


import json
import pandas as pd
import pvlib as pvl
import re
import os

from config import setup_logger

"""logging"""
log = setup_logger()


def search_dbs(path):
    """interactive db search tool
    parameters
    ___________
    path : 'str'
        relative directory to save results in as json

    """
    DB_NAMES = ['CECInverter', 'CECMod', 'SandiaMod', 'ADRInverter']
    dbs = {}
    for db in DB_NAMES:
        dbs[db] = pvl.pvsystem.retrieve_sam(db)

    print("enter 'str' to extend keywordlist to search dbs")
    print("enter '-' to clear keywordlist")
    print("enter 'DONE' to export results as json")
    print("enter 'STOP' to stop")

    keywordlist = []
    input_key = input()
    while input_key not in ['SAVE', 'STOP']:
        for char in input_key:
            if not isinstance(char, str):
                print('no good input key! will pass empty str')
                input_key = ''
        if input_key == '-':
            keywordlist = []
            print('Cleared keyword list')
        else:
            input_key = re.split(',| |_', input_key)
            if len(input_key) < 2:
                keywordlist.extend(input_key)
            else:
                keywordlist.extend(input_key)

            print('#########')
            print(keywordlist)

            results = {}
            for name, db in dbs.items():
                temp = [col for col, specs in db.iteritems() if all(key in col for key in keywordlist)]
                if len(temp) >= 1:
                    results[name] = temp

            for name, db in results.items():
                print('---------')
                print(name)
                print('---------')
                print(db)
        input_key = input()
    if input_key == 'STOP':
        print('operation aborted')
    if input_key == 'SAVE':

        output_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), path)
        if not os.path.isdir(output_dir):
            os.makedirs(output_dir)

        with open(output_dir + '/db_results.json', 'w') as fp:
            json.dump(results, fp, sort_keys=True, indent=4)
        log.info('Saved results to %s'%output_dir)