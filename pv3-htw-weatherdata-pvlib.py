import pandas as pd
import os
from datetime import timedelta
import pvlib
from pvlib.pvsystem import PVSystem
from pvlib.location import Location


def setup_converter_dataframe(converter, weather_data):
    """
    Reads HTW converter data from original files for given converter and sets
    up a dataframe.

    Parameters
    ----------
    converter : String
        Converter to set up the dataframe for. Possible choices are 'wr1',
        'wr2', 'wr3', 'wr4' and 'wr5'.
    weather_data : String
        Weather data that is used for calculated feed-in. The HTW data
        is resampled depending on the weather data. Possible choices are
        'open_FRED' and 'MERRA'.

    Returns
    --------
    pandas.DataFrame
        DataFrame with time series for feed-in etc..

    """
    file_directory = 'data/htw_2015/einleuchtend_data_2015'
    data = pd.read_csv(
        os.path.join(file_directory,
                     'einleuchtend_wrdata_2015_{}.csv'.format(converter)),
        sep=';', header=[0], index_col=[0], parse_dates=True)
    # resample to same resolution as weather data
    if weather_data == 'open_FRED':
        data = data.resample('30Min', loffset=timedelta(hours=0.25)).mean()
    elif weather_data == 'MERRA':
        data = data.resample('60Min', base=30,
                             loffset=timedelta(hours=0.5)).mean()
    data = data.tz_localize('Etc/GMT-1')
    data = data.tz_convert('Europe/Berlin')
    return data


def setup_weather_dataframe(weather_data):
    """
    Reads HTW weather data from original file and sets up a dataframe.

    Parameters
    ----------
    weather_data : String
        Weather data that is used for calculated feed-in. The HTW data
        is resampled depending on the weather data. Possible choices are
        'open_FRED' and 'MERRA'.

    Returns
    --------
    pandas.DataFrame
        DataFrame with time series for GHI and GNI in W/m², wind speed in m/s
        and air temperature in °C.

    """
    file_directory = 'data/htw_2015/einleuchtend_data_2015'
    data = pd.read_csv(
        os.path.join(file_directory, 'htw_wetter_weatherdata_2015.csv'),
        sep=';', header=[0], index_col=[0], parse_dates=True)
    # select and rename columns
    columns = {'G_hor_CMP6': 'ghi',
               'G_gen_CMP11': 'gni',
               'v_Wind': 'wind_speed',
               'T_Luft': 'temp_air'}
    data = data[list(columns.keys())]
    data.rename(columns=columns, inplace=True)
    # resample to same resolution as weather data
    if weather_data == 'open_FRED':
        data = data.resample('30Min', loffset=timedelta(hours=0.25)).mean()
    elif weather_data == 'MERRA':
        data = data.resample('60Min', base=30,
                             loffset=timedelta(hours=0.5)).mean()
    data = data.tz_localize('Etc/GMT-1') # GMT+1??
    data = data.tz_convert('Europe/Berlin')
    return data


def setup_pvlib_location_object():
    """
    Sets up pvlib Location object for HTW.

    Returns
    -------
    :pvlib:`Location`

    """
    return Location(latitude=52.456032, longitude=13.525282,
                    tz='Europe/Berlin', altitude=60, name='HTW Berlin')


def setup_htw_pvlib_pvsystem(converter_number):
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
