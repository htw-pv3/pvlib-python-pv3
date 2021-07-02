#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
HTW-PV3 - Create pvlib model for SONNJA



SPDX-License-Identifier: AGPL-3.0-or-later
"""

__copyright__ = "© Ludwig Hülk"
__license__ = "GNU Affero General Public License Version 3 (AGPL-3.0)"
__url__ = "https://www.gnu.org/licenses/agpl-3.0.en.html"
__author__ = "Ludee;"
__version__ = "v0.0.2"

import pvlib
from pvlib.location import Location
from pvlib.pvsystem import PVSystem
from pvlib.modelchain import ModelChain

from settings import HTW_LAT, HTW_LON

import logging
log = logging.getLogger(__name__)


def setup_pvlib_location_object():
    """
    Sets up pvlib Location object for HTW.

    Returns
    -------
    :pvlib:`Location`

    """
    return Location(latitude=HTW_LAT, longitude=HTW_LON,
                    tz='Europe/Berlin', altitude=80, name='HTW Berlin')


def setup_htw_pvlib_pvsystems(converter_number):
    """
    Sets up pvlib PVSystem for HTW Modules.

    Parameters
    -----------
    converter_number : :obj:`str`
        HTW converter number. Possible options are 'wr1', 'wr2', 'wr3', 'wr4',
        'wr5'.

    Returns
    -------
    :pvlib:`PVSystem`

    """

    # get module and inverter parameters
    sandia_modules = pvlib.pvsystem.retrieve_sam('SandiaMod')
    sandia_inverters = pvlib.pvsystem.retrieve_sam('sandiainverter')
    CEC_modules = pvlib.pvsystem.retrieve_sam('CECMod')
    CEC_inverters = pvlib.pvsystem.retrieve_sam('sandiainverter')

    inv_sma = 'SMA_Solar_Technology_AG__SB3000HFUS_30___240V_240V__CEC_2011_'
    inv_danfoss = 'Danfoss_Solar__DLX_2_9_UL__240V__240V__CEC_2013_'

    # module 1 - Schott aSi 105W / Danfoss DLX 2.9
    if converter_number == 'wr1':
        pass
    # module 2 - Aleo S19 285W / Danfoss DLX 2.9 'Aleo_Solar_S19H270' CEC
    elif converter_number == 'wr2':
        pass

    # module 3 - Aleo S18 240W / Danfoss DLX 2.9
    elif converter_number == 'wr3':
        pv_module = PVSystem(module='aleo_solar_S18_240', inverter=inv_danfoss,
                             module_parameters=CEC_modules[
                                 'aleo_solar_S18_240'],
                             inverter_parameters=CEC_inverters[inv_danfoss],
                             surface_tilt=14.57, surface_azimuth=215.,
                             albedo=0.2,
                             modules_per_string=14, strings_per_inverter=1,
                             name='HTW_module_3')
        pv_module.module_parameters['EgRef'] = 1.121
        pv_module.module_parameters['dEgdT'] = -0.0002677
        pv_module.module_parameters['alpha_sc'] = 0.04

    # module 4 - Aleo S19 245W / SMA SB 3000HF-30
    elif converter_number == 'wr4':
        pv_module = PVSystem(module='Aleo_Solar_S19U245_ulr', inverter=inv_sma,
                             module_parameters=CEC_modules[
                                 'Aleo_Solar_S19U245_ulr'],
                             inverter_parameters=CEC_inverters[inv_sma],
                             surface_tilt=14.57, surface_azimuth=215.,
                             albedo=0.2,
                             modules_per_string=13, strings_per_inverter=1,
                             name='HTW_module_4')
        pv_module.module_parameters['EgRef'] = 1.121
        pv_module.module_parameters['dEgdT'] = -0.0002677
        pv_module.module_parameters['alpha_sc'] = 0.03
    # module 5 - Schott aSi 105W / SMA SB 3000HF-30
    elif converter_number == 'wr5':
        pass
    return pv_module


def setup_htw_pvsystem_wr1():

    # Download parameters for pv and inverters
    sam_modules = pvlib.pvsystem.retrieve_sam('SandiaMod')
    CEC_inverters = pvlib.pvsystem.retrieve_sam('sandiainverter')

    converter_number = 'wr1'
    inv_danfoss = 'Danfoss_Solar__DLX_2_9_UL__240V__240V__CEC_2013_'
    pv1_module = 'Schott_Solar_ASE_100_ATF_34__100___1999__E__'

    model_wr1 = PVSystem(module=pv1_module,
                         inverter=inv_danfoss,
                         )


#def setup_htw_pvsystem_wr2():

def setup_htw_pvsystem_wr3():

    # Download parameters for pv and inverters
    CEC_modules = pvlib.pvsystem.retrieve_sam('CECMod')
    CEC_inverters = pvlib.pvsystem.retrieve_sam('sandiainverter')
    sam_adr_inv = pvlib.pvsystem.retrieve_sam('ADRInverter')

    converter_number = 'wr3'
    inv_danfoss = 'Danfoss_Solar__DLX_2_9_UL__240V__240V__CEC_2013_'
    pv3_module = 'Aleo_Solar_P18y255'

    model_wr3 = PVSystem(module=pv3_module,
                         inverter=inv_danfoss,
                         module_parameters=CEC_modules[pv3_module],
                         inverter_parameters=sam_adr_inv[inv_danfoss],
                         surface_tilt=14.57,
                         surface_azimuth=215.,
                         albedo=0.2,
                         modules_per_string=14,
                         strings_per_inverter=1,
                         name='HTW_WR3')

    return model_wr3


def setup_modelchain(pv_system, location):

    mc = ModelChain(system=pv_system, location=location,
                    aoi_model='no_loss', spectral_model='no_loss')
    return mc


def run_modelchain(mc, weather_data):

    mc.run_model(weather=weather_data)

    return mc