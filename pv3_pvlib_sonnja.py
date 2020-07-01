import pandas as pd
import matplotlib.pyplot as mpl
import numpy as np
import os
from collections import OrderedDict

import pvlib

from pvlib.modelchain import ModelChain
from pvlib import irradiance

import read_htw_data
import get_weather_data
import analysis_tools
import tools


def reindl(ghi, i0_h, elevation):
    """
    Reindl model to calculate DNI and DHI from GHI and I0_h.

    Parameters
    -----------
    ghi : :pandas:`DataFrame` or :numpy:`array`
        Time series for global horizontal irradiance in W/m².
    i0_h : :pandas:`DataFrame` or :numpy:`array`
        Time series for irradiance on top of atmosphere in W/m².
    elevation : :obj:`float`
        Elevation of location in m.

    Returns
    -------
    :collections:`OrderedDict`
        Dictionary with time series for DNI, DHI and clearness index kt.

    """

    elevation = pvlib.tools.sind(elevation)

    # calculate clearness index kt
    kt = np.maximum(0, ghi / (i0_h * elevation))

    # calculate diffuse fraction DHI/GHI
    # for kt <= 0.3
    df = 1.02 - 0.254 * kt + 0.0123 * elevation
    # for kt > 0.3 and kt <= 0.78
    df = np.where((kt > 0.3) & (kt <= 0.78),
                  np.fmin(0.97, np.fmax(
                      0.1, 1.4 - 1.794 * kt + 0.177 * elevation)),
                  df)
    # for kt > 0.78
    df = np.where(kt > 0.78, np.fmax(0.1, 0.486 * kt + 0.182 * elevation), df)

    # eliminate extreme data according to limits Case 1 and Case 2 in Reindl
    df = np.where(((df < 0.9) & (kt < 0.2)) |
                  ((df > 0.8) & (kt > 0.6)) |
                  (df > 1) | (ghi - i0_h > 0), 0, df)

    dhi = df * ghi
    dni = (ghi - dhi) / elevation

    data = OrderedDict()
    data['dni'] = dni
    data['dhi'] = dhi
    data['kt'] = kt

    if isinstance(ghi, pd.Series):
        data = pd.DataFrame(data)

    return data


def apply_decomposition_model(weather_df, model, location):
    """
    Uses the specified decomposition model to calculate DNI and DHI.

    Parameters
    ----------
    weather_df : :pandas:`DataFrame`
         Weather DataFrame containing all variables needed to apply the
         decomposition model. See model functions for more information.
    model : :obj:`str`
        Decomposition model to use. Choose from 'reindl', 'erbs' or 'disc'.
    location : :pvlib:`Location`

    Returns
    -------
    :pandas:`DataFrame`
     DataFrame with DNI and DHI.

    """

    solar_position = location.get_solarposition(
        weather_df.index, pressure=weather_df['pressure'].mean(),
        temperature=weather_df['temp_air'].mean())

    if model == 'reindl':

        solar_position = location.get_solarposition(
            weather_df.index, pressure=weather_df['pressure'].mean(),
            temperature=weather_df['temp_air'].mean())

        df = reindl(weather_df.ghi, weather_df.i0_h, solar_position.elevation)
        df['dni_corrected'] = irradiance.dni(
            weather_df['ghi'], df['dhi'], solar_position.zenith,
            clearsky_dni=location.get_clearsky(
                weather_df.index, solar_position=solar_position).dni,
            clearsky_tolerance=1.1,
            zenith_threshold_for_zero_dni=88.0,
            zenith_threshold_for_clearsky_limit=80.0)

    elif model == 'erbs':

        df = irradiance.erbs(weather_df.ghi, solar_position.zenith,
                             weather_df.index)
        df['dni_corrected'] = irradiance.dni(
            weather_df['ghi'], df['dhi'], solar_position.zenith,
            clearsky_dni=location.get_clearsky(
                weather_df.index, solar_position=solar_position).dni,
            clearsky_tolerance=1.1,
            zenith_threshold_for_zero_dni=88.0,
            zenith_threshold_for_clearsky_limit=80.0)

    elif model == 'disc':

        df = irradiance.disc(weather_df.ghi, solar_position.zenith,
                             weather_df.index, weather_df.pressure.mean())
        df['dhi'] = weather_df.ghi - df.dni * pvlib.tools.cosd(
            solar_position.zenith)
        df['gni'] = df.dni + df.dhi

    return df


def compare_decomposition_models(merra_df, location, htw_weather_df,
                                 plot=False,
                                 plot_directory='plot/decomposition'):
    """
    Compares the decomposition models Reindl, Erbs and Disc. Calculates
    correlation and RMSE and optionally plots these plus a winter and summer
    week.

    Parameters
    ----------
    merra_df : :pandas:`DataFrame`
         MERRA weather DataFrame.
    location : :pvlib:`Location`
    htw_weather_df : :pandas:`DataFrame`
         HTW weather DataFrame.
    plot : Boolean
        If true plots are created. Default: False.
    plot_directory : :obj:`str`
        Path to directory plot is saved to.

    Returns
    -------
    :pandas:`DataFrame`
        DataFrame with GNI and corrected GNI of the three models.

    """
    # hard-coded inputs
    weather_data = 'MERRA'
    measured_data = 'HTW'
    weeks = [('1/25/2015', '2/1/2015'), ('6/2/2015', '6/8/2015')]
    resample_rule = '1W'

    # reindl
    df_reindl = apply_decomposition_model(merra_df, 'reindl',
                                          location=location)
    df_reindl['gni'] = (df_reindl.dni + df_reindl.dhi).fillna(0)
    df_reindl['gni_corrected'] = (df_reindl.dni_corrected +
                                  df_reindl.dhi).fillna(0)

    # erbs
    df_erbs = apply_decomposition_model(merra_df, 'erbs', location=location)
    df_erbs['gni'] = df_erbs.dni + df_erbs.dhi
    df_erbs['gni_corrected'] = df_erbs.dni_corrected + df_erbs.dhi

    # disc
    df_disc = apply_decomposition_model(merra_df, 'disc', location=location)

    # combine dataframes
    df_comp = df_reindl.loc[:, ['gni', 'gni_corrected']].join(
        df_erbs.loc[:, ['gni', 'gni_corrected']],
        how='outer', rsuffix='_erbs', lsuffix='_reindl')
    df_comp = df_comp.join(df_disc.gni.rename('gni_disc').to_frame(),
                           how='outer', rsuffix='_disc')

    # calculate correlation and rmse
    parameter_list = ['gni_disc', 'gni_corrected_reindl', 'gni_corrected_erbs']
    count = 0
    for param in parameter_list:
        df = htw_weather_df['gni'].to_frame().join(
            df_comp[param].to_frame(), how='outer')
        corr = analysis_tools.correlation_tmp(
            df, resample_rule, min_count=100).rename(
            'corr_gni_htw_{}'.format(param))
        var = analysis_tools.variability(
            df, resample_rule, min_count=100).rename(
            'rmse_gni_htw_{}'.format(param))
        corr_year = np.round(analysis_tools.correlation_tmp(df, '1Y').iloc[0],
                             2)
        var_year = np.round(analysis_tools.variability(df, '1Y').iloc[0], 2)
        if plot:
            for week in weeks:
                filename = 'decomposition_comparison_week_{}_to_{}_{}_{}_{}_' \
                           'annual_corr_{}_annual_RMSE_{}'.format(
                    week[0].replace('/', '_'), week[1].replace('/', '_'),
                    param, weather_data, measured_data, corr_year, var_year)
                plot_time_range(df.fillna(0), week, filename, plot_directory,
                                weather_data)
        if count == 0:
            corr_df = corr.to_frame()
            var_df = var.to_frame()
        else:
            corr_df = corr_df.join(corr.to_frame())
            var_df = var_df.join(var.to_frame())
        count += 1

    if plot:
        # plot correlation
        corr_df.plot(title='Correlation')
        mpl.ylabel('Correlation coefficient')
        mpl.savefig(
            os.path.join(
                plot_directory, 'decomposition_comparison_correlation_'
                                '{}_{}_{}.png'.format(
                    resample_rule, weather_data, measured_data)))
        mpl.clf()
        # plot RMSE
        var_df.plot(title='RMSE')
        mpl.ylabel('RMSE in W/m²')
        mpl.savefig(
            os.path.join(
                plot_directory, 'decomposition_comparison_RMSE_'
                                '{}_{}_{}.png'.format(
                    resample_rule, weather_data, measured_data)))
        # plot weeks
        df_week = df_comp.loc[:, ['gni_disc', 'gni_corrected_reindl',
                                  'gni_corrected_erbs']].fillna(0).join(
            htw_weather_df['gni'].to_frame())
        for week in weeks:
            filename = 'decomposition_comparison_week_{}_to_{}_' \
                       'GNI_all_models_{}_{}'.format(
                week[0].replace('/', '_'), week[1].replace('/', '_'),
                weather_data, measured_data)
            plot_time_range(df_week, week, filename, plot_directory,
                            weather_data)
    return df_comp


def load_merra_data(year, lat, lon, directory):
    """
    Loads MERRA weather data.

    Parameters
    -----------
    year : :obj:`int`
    lat : :obj:`float`
    lon : :obj:`float`
    directory : :obj:`str`
        Path to MERRA csv file.

    Returns
    --------
    :pandas:`DataFrame`
        DataFrame with weather data.

    """
    # read csv file
    merra_df = pd.read_csv(
        os.path.join(directory, 'weather_data_GER_{}.csv'.format(year)),
        header=[0], index_col=[0], parse_dates=True)
    # get closest coordinates to given location
    lat_lon = tools.get_closest_coordinates(merra_df, [lat, lon])
    # get weather data for closest location
    df = merra_df[(merra_df['lon'] == lat_lon['lon']) &
                  (merra_df['lat'] == lat_lon['lat'])]
    # convert time index to local time
    df.index = df.index.tz_localize('UTC').tz_convert('Europe/Berlin')
    # rename columns to fit needs of pvlib
    df.rename(columns={'T': 'temp_air', 'v_50m': 'wind_speed', 'p': 'pressure',
                       'SWTDN': 'i0_h', 'SWGDN': 'ghi'}, inplace=True)
    # convert temperature to °C
    df.loc[:, 'temp_air'] = df.temp_air - 273.15
    return df


def get_index(start_date, end_date, weather_data):
    """
    Sets up index to select date range from data set.

    Parameters
    -----------
    start_date :  :obj:`str`
        String with start of date range, e.g. '1/25/2015'.
    end_date :  :obj:`str`
        String with end of date range.
    weather_data :  :obj:`str`
        Weather data set used. Possible choices are 'MERRA' or 'open_FRED'.

    Returns
    -------
    :pandas:`DateTimeIndex`

    """
    if weather_data == 'open_FRED':
        index = pd.date_range(start=start_date, end=end_date,
                              freq='30Min', tz='UTC') \
                - pd.Timedelta(minutes=15)
    elif weather_data == 'MERRA':
        index = pd.date_range(start=start_date, end=end_date,
                              freq='60Min', tz='UTC')
    return index


def plot_time_range(data, time_range, filename, plot_directory,
                    weather_data, ylabel=None, legend_loc=None, title=None):
    """
    Plots data for the given time range.

    Parameters
    -----------
    data : :pandas:`DataFrame`
        Data to plot.
    time_range : :obj:`tuple`
        Tuple with start and end date, e.g. ('1/25/2015', '2/1/2015').
    filename : :obj:`str`
    plot_directory : :obj:`str`
        Path to directory plot is saved to.
    weather_data : :obj:`str`
        Weather data set used. Possible choices are 'MERRA' or 'open_FRED'.
    ylabel : :obj:`str`, optional
        Label of y-axis. Default: None.
    legend_loc : :obj:`int`, optional
        Location of legend.
    title : :obj:`str`, optional

    """

    # set frequency of index
    index = get_index(time_range[0], time_range[1], weather_data)

    data.loc[index, :].plot(title=title)
    if ylabel:
        mpl.ylabel(ylabel)
    if legend_loc:
        mpl.legend(loc=legend_loc)
    mpl.savefig(os.path.join(plot_directory, '{}.png'.format(filename)))





def compare_parameters_2(dict, parameter, resample_rule, plot_directory):
    """
    Calculates and plots correlation and RMSE between three time series.

    :param df:
    :param parameter:
    :param resample_rule:
    :param plot_directory:
    :return:
    """
    corr = {}
    corr_annual = {}
    rmse = {}
    rmse_annual = {}
    for key in dict.keys():

        # calculate correlation
        corr[key] = analysis_tools.correlation_tmp(
            dict[key], resample_rule=resample_rule)
        corr_annual[key] = np.round(analysis_tools.correlation_tmp(
            dict[key], resample_rule='1Y').iloc[0], 2)

        # calculate RMSE
        rmse[key] = analysis_tools.variability(
            dict[key], resample_rule=resample_rule)
        rmse_annual[key] = np.round(analysis_tools.variability(
            dict[key], resample_rule='1Y').iloc[0], 2)

    # plot correlation
    corr['MERRA'].plot(legend=True)
    corr['open_FRED'].plot(legend=True, grid=True,
                           title='Correlation {}'.format(corr_annual))
    mpl.savefig(os.path.join(
        plot_directory, '{}_correlation_{}.png'.format(
            parameter, resample_rule)))
    mpl.clf()
    
    # plot RMSE
    rmse['MERRA'].plot(legend=True)
    rmse['open_FRED'].plot(legend=True, grid=True,
                           title='RMSE {}'.format(rmse_annual))
    mpl.savefig(os.path.join(
        plot_directory, '{}_rmse_{}.png'.format(
            parameter, resample_rule)))
    mpl.clf()


def plot_time_range_multiple_datasets(data_dict, column, time_range, filename,
                                      plot_directory, figsize=None):
    """
    Plots data for the given time range and weather data sets.

    Parameters
    -----------
    data_dict : :obj:`dict`
        Dictionary where keys specify the weather data set and the
        corresponding values are :pandas:`DataFrame` with data to plot.
    time_range : :obj:`tuple`
        Tuple with start and end date, e.g. ('1/25/2015', '2/1/2015').
    filename : :obj:`str`
    plot_directory : :obj:`str`
        Path to directory plot is saved to.
    figsize : :obj:`list`, optional
        List with height and breadth of figure, e.g. [20, 15]. Default: None.

    """

    weather_data_sets = data_dict.keys()

    # set frequency of index
    index = {}
    for data_set in weather_data_sets:
        index[data_set] = get_index(time_range[0], time_range[1], data_set)

    data_dict[data_set].loc[index[data_set], :].plot(
        legend=True, figsize=figsize)
    for data_set in weather_data_sets[1:-1]:
        data_dict[data_set].loc[index[data_set], column].plot(
            legend=True, grid=True)
    mpl.savefig(os.path.join(plot_directory, '{}.png'.format(filename)))


def calculate_dni_pvlib(weather_df, corrected=True):
    """
    Calculates DNI from open_FRED GHI and DHI using the pvlib.

    :param weather_df:
    :param corrected:
    :return:
    """

    # calculate DNI
    times = weather_df.index
    location = read_htw_data.setup_pvlib_location_object()
    solarposition = location.get_solarposition(
        times, pressure=None, temperature=weather_df['temp_air'])
    if corrected:
        # calculate corrected DNI
        clearsky = location.get_clearsky(times, solar_position=solarposition)
        dni = irradiance.dni(weather_df['ghi'], weather_df['dhi'],
                             zenith=solarposition['zenith'],
                             clearsky_dni=clearsky['dni'],
                             clearsky_tolerance=1.1,
                             zenith_threshold_for_zero_dni=88.0,
                             zenith_threshold_for_clearsky_limit=80.0)
    else:
        dni = (weather_df['ghi'] - weather_df['dhi']) / np.cos(
            np.radians(solarposition['zenith']))

    # setup df with calculated and Fred DNI
    dni.name = 'dni'
    df = weather_df['dni'].to_frame().join(
        dni.to_frame(), lsuffix='_fred', rsuffix='_pvlib')
    dni.set_index('time', inplace=True)

    return df


def setup_and_run_modelchain(pv_system, location, weather_data):

    mc = ModelChain(system=pv_system, location=location,
                    aoi_model='no_loss', spectral_model='no_loss')
    mc.run_model(weather_data.index, weather=weather_data)
    return mc


def compare_weather_data_fred_htw(fred_weather_data):

    def setup_correlation_df(htw_weather_data_df, reanalysis_weather_data_df,
                             parameter, weather_data='open_FRED',
                             corrected=True):
        # Note: in case of DNI FRED DNI and calculated DNI (calculated from FRED
        # GHI and DHI) are compared; in case of GHI and GNI HTW (measured) values
        # are compared to FRED (calculated) values

        # setup dataframe with given parameter of HTW and FRED weather dataset
        if parameter == 'dni':
            df = calculate_dni_pvlib(reanalysis_weather_data_df, weather_data,
                                     corrected)
        else:
            df = reanalysis_weather_data_df[parameter].to_frame().join(
                htw_weather_data_df[parameter].to_frame(),
                lsuffix='_fred', rsuffix='_htw')
        return df

    def compare_parameters(df, parameter, resample_rule, plot_directory):
        """
        Calculates and plots correlation and RMSE between two time series.

        :param df:
        :param parameter:
        :param resample_rule:
        :param plot_directory:
        :return:
        """
        # calculate correlation
        corr = analysis_tools.correlation_tmp(df, resample_rule=resample_rule)

        # plot correlation
        corr.plot()
        mpl.savefig(os.path.join(
            plot_directory, '{}_correlation_{}.png'.format(
                parameter, resample_rule)))

        # calculate RMSE
        rmse = analysis_tools.variability(df, resample_rule=resample_rule)

        # plot correlation
        rmse.plot()
        mpl.savefig(os.path.join(
            plot_directory, '{}_rmse_{}.png'.format(
                parameter, resample_rule)))

    # ghi
    parameter = 'ghi'
    resample_rule = '1M'
    df = setup_correlation_df(htw_weather_data, fred_weather_data, parameter,
                              weather_data)
    compare_parameters(df, parameter, resample_rule, plot_directory)
    # winter_week = ('1/25/2015', '2/1/2015'),
    # summer_week = ('6/2/2015', '6/8/2015')
    plot_week(parameter, weather_data, measured_data, plot_directory)

    # gni
    parameter = 'gni'
    resample_rule = '1M'
    df = setup_correlation_df(htw_weather_data, fred_weather_data, parameter,
                              weather_data)
    compare_parameters(df, parameter, resample_rule, plot_directory)
    plot_week(parameter, weather_data, measured_data, plot_directory)

    # dni
    parameter = 'dni'
    resample_rule = '1M'
    weather_data = 'open_FRED'
    corrected = True
    df = setup_correlation_df(htw_weather_data, fred_weather_data, parameter,
                              weather_data, corrected=corrected)
    compare_parameters(df, parameter + '_corrected', resample_rule,
                       plot_directory)
    plot_week(parameter + '_corrected', weather_data, plot_directory)

    corrected = False
    df = setup_correlation_df(htw_weather_data, fred_weather_data, parameter,
                              weather_data, corrected=corrected)
    compare_parameters(df, parameter + '_uncorrected', resample_rule,
                       plot_directory)
    plot_week(parameter + '_uncorrected', weather_data, plot_directory)


def compare_feedin_htw(converters, weather_data_sets):
    plot_directory = 'plot'
    resample_rule = '1W'

    ###########################################################################
    # read HTW converter data
    ###########################################################################

    htw_wr_data = {}
    for converter in converters:
        htw_wr_data[converter] = {}
        for weather_data_set in weather_data_sets:
            htw_wr_data[converter][weather_data_set] = \
                read_htw_data.setup_converter_dataframe(
                    converter, weather_data_set)

    ###########################################################################
    # get weather data HTW
    ###########################################################################

    htw_weather_data = {}
    for weather_data_set in weather_data_sets:
        htw_weather_data[weather_data_set] = \
            read_htw_data.setup_weather_dataframe(weather_data_set)

    ###########################################################################
    # setup location
    ###########################################################################

    location = read_htw_data.setup_pvlib_location_object()

    ###########################################################################
    # get weather data
    ###########################################################################

    weather_data_dict = {}
    # open_FRED
    path = 'data/Fred/BB_2015'
    filename = 'fred_data_2015_htw.csv'
    weather_data_dict['open_FRED'] = \
        get_weather_data.read_of_weather_df_pvlib_from_csv(
            path, filename, coordinates=None)

    # MERRA
    weather_data_dict['MERRA'] = load_merra_data(
        2015, location.latitude, location.longitude, 'data/Merra')
    decomposition_df = apply_decomposition_model(
        weather_data_dict['MERRA'], 'erbs', location)
    try:
        weather_data_dict['MERRA']['dni'] = \
            decomposition_df.dni_corrected.fillna(0)
    except:
        weather_data_dict['MERRA']['dni'] = \
            decomposition_df.dni.fillna(0)
    weather_data_dict['MERRA']['dhi'] = decomposition_df.dhi.fillna(0)
    weather_data_dict['MERRA']['dirhi'] = \
        weather_data_dict['MERRA'].ghi - weather_data_dict['MERRA'].dhi
    weather_data_dict['MERRA']['gni'] = \
        weather_data_dict['MERRA'].dhi + weather_data_dict['MERRA'].dni

    gni_dict = {}
    gni_dict['MERRA'] = weather_data_dict['MERRA'].gni.to_frame().join(
        htw_weather_data['MERRA'].gni.to_frame(), rsuffix='_htw',
        lsuffix='_merra')
    weather_data_dict['open_FRED']['gni'] = \
        weather_data_dict['open_FRED']['dni'] + \
        weather_data_dict['open_FRED']['dhi']
    gni_dict['open_FRED'] = weather_data_dict['open_FRED'].gni.to_frame().join(
        htw_weather_data['open_FRED'].gni.to_frame(), rsuffix='_htw',
        lsuffix='_open_FRED')
    gni_dict['open_FRED'] = \
        gni_dict['open_FRED'].loc[
            gni_dict['open_FRED'].index.year == 2015]
    compare_parameters_2(
        gni_dict, 'GNI', resample_rule, plot_directory)

    winter_week = ('3/9/2015', '3/16/2015')
    index = {}
    index['open_FRED'] = pd.date_range(
        start=winter_week[0], end=winter_week[1], freq='30Min', tz='UTC') \
                         - pd.Timedelta(minutes=15)
    index['MERRA'] = pd.date_range(start=winter_week[0], end=winter_week[1],
                                   freq='60Min', tz='UTC')

    gni_dict['MERRA'].loc[index['MERRA'], :].plot(legend=True)
    gni_dict['open_FRED'].loc[index['open_FRED'],
                          'gni_open_FRED'].plot(legend=True, grid=True)
    mpl.savefig(os.path.join(plot_directory, '{}_march_week.png'.format(
        'GNI')))

    # dhi_monthly_sums = {}
    # dhi_monthly_sums['MERRA'] = weather_data_dict['MERRA'].dhi.resample(
    #     '1M').sum()
    # dhi_monthly_sums['open_FRED'] = weather_data_dict[
    #     'open_FRED'].dhi.resample('1H').mean().resample('1M').sum()
    #htw_weather_data['open_FRED'].gni.resample('1H').mean().resample('1M').sum()

    ###########################################################################
    # setup modules
    ###########################################################################

    modules = {}
    for converter in converters:
        modules[converter] = read_htw_data.setup_htw_pvlib_pvsystem(converter)

    ###########################################################################
    # call modelchain with reanalysis data
    ###########################################################################

    feedin = {}
    for converter in converters:
        feedin[converter] = {}
        for weather_data_set in weather_data_sets:
            # set up modelchain
            mc = setup_and_run_modelchain(
                modules[converter], location,
                weather_data_dict[weather_data_set])

            # set up feed-in
            feedin[converter][weather_data_set] = mc.dc.p_mp.to_frame().join(
                htw_wr_data[converter][weather_data_set]['P_DC'].to_frame())
            feedin[converter][weather_data_set].rename(
                columns={'p_mp': 'energy_calculated_{}'.format(
                    weather_data_set),
                         'P_DC': 'energy_measured'},
                inplace=True)
            feedin[converter][weather_data_set] = \
                feedin[converter][weather_data_set].loc[
                    feedin[converter][weather_data_set].index.year == 2015]

        # calculate monthly correlation and RMSE for feed-in
        parameter = 'pv_feedin_{}'.format(converter)
        compare_parameters_2(
            feedin[converter], parameter, resample_rule, plot_directory)

        plot_week_2(feedin[converter], parameter, plot_directory)

        # compare energy
        monthly_energy = {}
        monthly_energy['MERRA'] = feedin[converter][
            'MERRA'].resample(resample_rule).sum()
        monthly_energy['open_FRED'] = feedin[converter][
            'open_FRED'].resample(resample_rule).sum() / 2
        monthly_energy['MERRA'].plot(legend=True)
        monthly_energy['open_FRED'].loc[:, 'energy_calculated_open_FRED'].plot(
            legend=True, grid=True, title='Energy feed-in')
        mpl.savefig(os.path.join(plot_directory,
                                 'pv_feedin_{}_energy.png'.format(
                                     converter)))
        mpl.clf()

    ###########################################################################
    # call modelchain with HTW data
    ###########################################################################

    htw_weather_data_modified = {}
    for weather_data_set in weather_data_sets:
        htw_weather_data_modified[weather_data_set] = weather_data_dict[
            weather_data_set].copy()
        htw_weather_data_modified[weather_data_set]['ghi'] = \
            htw_weather_data[weather_data_set]['ghi']
        htw_weather_data_modified[weather_data_set]['dhi'] = \
            htw_weather_data_modified[weather_data_set]['ghi'] - \
            htw_weather_data_modified[weather_data_set]['dirhi']

    for converter in converters:
        for weather_data_set in weather_data_sets:
            # set up modelchain
            mc = setup_and_run_modelchain(
                modules[converter], location,
                htw_weather_data_modified[weather_data_set])

            # set up feed-in
            feedin[converter][weather_data_set] = mc.dc.p_mp.to_frame().join(
                htw_wr_data[converter][weather_data_set]['P_DC'].to_frame())
            feedin[converter][weather_data_set].rename(
                columns={'p_mp': 'energy_calculated_{}'.format(
                    weather_data_set),
                    'P_DC': 'energy_measured'},
                inplace=True)
            feedin[converter][weather_data_set] = \
                feedin[converter][weather_data_set].loc[
                    feedin[converter][weather_data_set].index.year == 2015]

        # calculate monthly correlation and RMSE for feed-in
        parameter = 'pv_feedin_{}_htw'.format(converter)
        compare_parameters_2(
            feedin[converter], parameter, resample_rule, plot_directory)

        plot_week_2(feedin[converter], parameter, plot_directory)

        # compare energy
        monthly_energy = {}
        monthly_energy['MERRA'] = feedin[converter][
            'MERRA'].resample(resample_rule).sum()
        monthly_energy['open_FRED'] = feedin[converter][
                                          'open_FRED'].resample(
            resample_rule).sum() / 2
        monthly_energy['MERRA'].plot(legend=True)
        monthly_energy['open_FRED'].loc[:,
        'energy_calculated_open_FRED'].plot(
            legend=True, grid=True, title='Energy feed-in')
        mpl.savefig(os.path.join(plot_directory,
                                 'pv_feedin_{}_energy_htw.png'.format(
                                     converter)))
        mpl.clf()


if __name__ == '__main__':

    # weather_data_sets = ['MERRA', 'open_FRED']
    # converters = ['wr3', 'wr4']
    # compare_feedin_htw(converters, weather_data_sets)

    year = 2015
    location = read_htw_data.setup_pvlib_location_object()
    merra_df = load_merra_data(year, location.latitude, location.longitude,
                               'data/Merra')
    fred_df = get_weather_data.read_of_weather_df_pvlib_from_csv(
        'data/Fred/BB_2015', 'fred_data_2015_htw.csv', coordinates=None)
    htw_weather_data = read_htw_data.setup_weather_dataframe(
        weather_data='MERRA')
    df_comp = compare_decomposition_models(
        merra_df, location, htw_weather_data, plot=True)
    # fred_df['gni_fred'] = fred_df.dni + fred_df.dhi
    # fred_df.ghi.to_frame().plot()
    # df_comp.loc[:, ['gni_disc', 'gni_corrected_reindl', 'gni_corrected_erbs']].plot()
    # mpl.savefig(os.path.join('plot/decomposition', 'test.png'))



    # ##############################################################################
    # # compare FRED and HTW weather data
    # ##############################################################################
    #
    # # ghi
    # parameter = 'ghi'
    # resample_rule = '1M'
    # df = setup_correlation_df(htw_weather_data, fred_weather_data, parameter,
    #                           weather_data)
    # compare_parameters(df, parameter, resample_rule, plot_directory)
    # plot_week(parameter, weather_data, measured_data, plot_directory)
    #
    # # gni
    # parameter = 'gni'
    # resample_rule = '1M'
    # df = setup_correlation_df(htw_weather_data, fred_weather_data, parameter,
    #                           weather_data)
    # compare_parameters(df, parameter, resample_rule, plot_directory)
    # plot_week(parameter, weather_data, measured_data, plot_directory)
    #
    # # dni
    # parameter = 'dni'
    # resample_rule = '1M'
    # weather_data = 'open_FRED'
    # corrected = True
    # df = setup_correlation_df(htw_weather_data, fred_weather_data, parameter,
    #                           weather_data, corrected=corrected)
    # compare_parameters(df, parameter + '_corrected', resample_rule,
    #                    plot_directory)
    # plot_week(parameter + '_corrected', weather_data, plot_directory)
    #
    # corrected = False
    # df = setup_correlation_df(htw_weather_data, fred_weather_data, parameter,
    #                           weather_data, corrected=corrected)
    # compare_parameters(df, parameter + '_uncorrected', resample_rule,
    #                    plot_directory)
    # plot_week(parameter + '_uncorrected', weather_data, plot_directory)
    #
