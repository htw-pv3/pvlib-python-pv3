import pvlib
import numpy as np


def get_sma_sb_3000hf():
    """
    Import the Inverter SMA SUNNY BOY 3000HF to pvlib

    :return:
    inverter dictionary, type: sandia model
    """
    # inverter efficiency at different power points (source: SMA WirkungDerat-TI-de-36 | Version 3.6)
    eta_min = [0, 0.942, 0.95, 0.951, 0.94, 0.932]  # P/P_max = 0, 0.2, 0.3, 0.5, 0.75, 1; U = 210V
    eta_nom = [0, 0.953, 0.961, 0.963, 0.96, 0.954]  # P/P_max = 0, 0.2, 0.3, 0.5, 0.75, 1; U = 530V
    eta_max = [0, 0.951, 0.959, 0.96, 0.96, 0.955]  # P/P_max = 0, 0.2, 0.3, 0.5, 0.75, 1; U = 560V
    # dc voltage at min, nom and max
    dc_voltage = [[210.], [530.], [560.]]
    # calculate dc power
    p_dc_nom = 3150
    p_dc = [0, 0.2 * p_dc_nom, 0.3 * p_dc_nom, 0.5 * p_dc_nom, 0.75 * p_dc_nom, 1 * p_dc_nom]
    p_ac_min = []
    p_ac_nom = []
    p_ac_max = []
    val_count = len(eta_min)

    # calculate ac power
    for i in range(val_count):
        p_ac_min.append(p_dc[i] * eta_min[i])
        p_ac_nom.append(p_dc[i] * eta_nom[i])
        p_ac_max.append(p_dc[i] * eta_max[i])

    ac_power = np.array(p_ac_min + p_ac_nom + p_ac_max)

    # save all necessary inverter data to a dictionary
    sma_sb_data = {
        "ac_power": ac_power,
        "dc_power": np.array(p_dc + p_dc + p_dc),  # Annahme: Strom bleibt in allen Punkten gleich
        "dc_voltage": np.array(dc_voltage[0] * val_count + dc_voltage[1] * val_count + dc_voltage[2] * val_count),
        "dc_voltage_level": np.array(["Vmin"] * val_count + ["Vnom"] * val_count + ["Vmax"] * val_count),
        "p_ac_0": 3000.,
        "p_nt": 1.
    }

    # call method that creates sandia inverter model
    inverter = pvlib.inverter.fit_sandia(sma_sb_data["ac_power"], sma_sb_data["dc_power"], sma_sb_data["dc_voltage"],
                                         sma_sb_data["dc_voltage_level"], sma_sb_data["p_ac_0"], sma_sb_data["p_nt"])
    return inverter


def get_danfoss_dlx_2_9():
    """
    Import the Inverter Danfoss DLX 2.9 to pvlib

    :return:
    inverter dictionary, type: sandia model
    """
    # inverter efficiency at different power points (source: PV*SOL)
    eta_min = [0, 0.953, 0.959, 0.963, 0.9612, 0.959]  # P/P_max = 0, 0.2, 0.3, 0.5, 0.75, 1; U = 210V
    eta_nom = [0, 0.961, 0.967, 0.971, 0.969, 0.967]  # P/P_max = 0, 0.2, 0.3, 0.5, 0.75, 1; U = 530V
    eta_max = [0, 0.952, 0.958, 0.962, 0.96, 0.958]  # P/P_max = 0, 0.2, 0.3, 0.5, 0.75, 1; U = 560V
    # dc voltage at min, nom and max
    dc_voltage = [[230.], [350.], [480.]]
    # calculate dc power
    p_dc_nom = 3750
    p_dc = [0, 0.2 * p_dc_nom, 0.3 * p_dc_nom, 0.5 * p_dc_nom, 0.75 * p_dc_nom, 1 * p_dc_nom]
    p_ac_min = []
    p_ac_nom = []
    p_ac_max = []
    val_count = len(eta_min)

    # calculate ac power
    for i in range(val_count):
        p_ac_min.append(p_dc[i] * eta_min[i])
        p_ac_nom.append(p_dc[i] * eta_nom[i])
        p_ac_max.append(p_dc[i] * eta_max[i])

    ac_power = np.array(p_ac_min + p_ac_nom + p_ac_max)

    # save all necessary inverter data to a dictionary
    sma_sb_data = {
        "ac_power": ac_power,
        "dc_power": np.array(p_dc + p_dc + p_dc),  # Annahme: Strom bleibt in allen Punkten gleich
        "dc_voltage": np.array(dc_voltage[0] * val_count + dc_voltage[1] * val_count + dc_voltage[2] * val_count),
        "dc_voltage_level": np.array(["Vmin"] * val_count + ["Vnom"] * val_count + ["Vmax"] * val_count),
        "p_ac_0": 2900.,
        "p_nt": 1.  # power consumed while inverter is not delivering AC power
    }

    # call method that creates sandia inverter model
    inverter = pvlib.inverter.fit_sandia(sma_sb_data["ac_power"], sma_sb_data["dc_power"], sma_sb_data["dc_voltage"],
                                         sma_sb_data["dc_voltage_level"], sma_sb_data["p_ac_0"], sma_sb_data["p_nt"])
    return inverter


def get_aleo_s18_240():
    """Import Aleo S18 240 W PV-Modul"""
    sam_cec_mod = pvlib.pvsystem.retrieve_sam('CECMod')
    aleo_s18_240 = sam_cec_mod['Aleo_Solar_S18y250'].copy()
    aleo_s18_240['STC'] = 240.
    aleo_s18_240['PTC'] = 215.04
    aleo_s18_240['V_mp_ref'] = 29.5
    aleo_s18_240['V_oc_ref'] = 37.0
    aleo_s18_240['I_mp_ref'] = 8.13
    aleo_s18_240['I_sc_ref'] = 8.65
    aleo_s18_240['alpha_sc'] = 0.04
    aleo_s18_240['beta_oc'] = -0.34
    aleo_s18_240['gamma_r'] = -0.46
    return aleo_s18_240
    # The PTC value was calculated by dividing the STC of the created module
    # by the STC of the reference module and multiplying it by the PTC of the reference module.
    # All other values were taken from the data sheet.

    # adding the specific Modul parameters for aleo_s19_245
def get_aleo_s19_245():
    """Import Aleo S19 245 W PV-Modul"""
    sam_cec_mod = pvlib.pvsystem.retrieve_sam('CECMod')
    aleo_s19_245 = sam_cec_mod['Aleo_Solar_S19Y270'].copy()
    aleo_s19_245['STC'] = 245.
    aleo_s19_245['PTC'] = 220.
    aleo_s19_245['V_mp_ref'] = 31.3
    aleo_s19_245['V_oc_ref'] = 37.1
    aleo_s19_245['I_mp_ref'] = 7.84
    aleo_s19_245['I_sc_ref'] = 8.48
    aleo_s19_245['alpha_sc'] = 0.03
    aleo_s19_245['beta_oc'] = -0.34
    aleo_s19_245['gamma_r'] = -0.48
    return aleo_s19_245
    # The PTC value was calculated by dividing the STC of the created module
    # by the STC of the reference module and multiplying it by the PTC of the reference module.
    # All other values were taken from the data sheet.

    # adding data for aleo_s19_285, even though the module is in the CEC-Database
def get_aleo_s19_285():
    """Import Aleo S19 285 W PV-Modul"""
    sam_cec_mod = pvlib.pvsystem.retrieve_sam('CECMod')
    aleo_s19_285 = sam_cec_mod['Aleo_Solar_S19y285'].copy()
    aleo_s19_285['STC'] = 285.
    aleo_s19_285['PTC'] = 261.25
    aleo_s19_285['V_mp_ref'] = 31.3
    aleo_s19_285['V_oc_ref'] = 39.2
    aleo_s19_285['I_mp_ref'] = 9.10
    aleo_s19_285['I_sc_ref'] = 9.73
    aleo_s19_285['alpha_sc'] = 0.05
    aleo_s19_285['beta_oc'] = -0.30
    aleo_s19_285['gamma_r'] = -0.43
    return aleo_s19_285
    # The PTC value was calculated by dividing the STC of the created module
    # by the STC of the reference module and multiplying it by the PTC of the reference module.
    # All other values were taken from the data sheet.

def get_schott_asi_105():
    """Import Schott a-Si 105 W PV-Modul"""
    sam_cec_mod = pvlib.pvsystem.retrieve_sam('CECMod')
    schott = sam_cec_mod['Bosch_Solar_Thin_Film_um_Si_plus_105'].copy()
    schott['I_sc_ref'] = 3.98
    schott['V_oc_ref'] = 41.0
    schott['I_mp_ref'] = 3.38
    schott['V_mp_ref'] = 31.1
    schott['STC'] = 105
    schott['PTC'] = 95
    schott['alpha_sc'] = 0.08
    schott['beta_oc'] = -0.33
    schott['gamma_r'] = -0.2
    schott['Length'] = 1.308
    schott['Width'] = 1.108
    schott['T_NOCT'] = 49
    return schott
    # The PTC value was calculated by dividing the STC of the created module
    # by the STC of the reference module and multiplying it by the PTC of the reference module.
    # All other values were taken from the data sheet.

if __name__ == "__main__":
    print('Show inverters')
    sma = get_sma_sb_3000hf()
    print(sma)
    dan = get_danfoss_dlx_2_9()
    print(dan)

    aleo_s18_240 = get_aleo_s18_240
    print(aleo_s18_240)
    aleo_s19_245 = get_aleo_s19_245
    print(aleo_s19_245)
    aleo_s19_285 = get_aleo_s19_285()
    print(aleo_s19_285)
    aleo_asi_105 = get_schott_asi_105()
    print(aleo_asi_105)
