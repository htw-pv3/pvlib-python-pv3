import pvlib
import numpy as np


def get_sma_sb_3000hf():
    """
    Import the Inverter SMA SUNNY BOY 3000HF to pvlib

    :return:
    inverter dictionary, type: sandia model
    """
    # inverter efficiency at different power points
    eta_min = [0, 0.945, 0.95, 0.947, 0.942, 0.931]  # P/P_max = 0, 0.2, 0.3, 0.5, 0.75, 1; U = 210V
    eta_nom = [0, 0.953, 0.962, 0.963, 0.96, 0.952]  # P/P_max = 0, 0.2, 0.3, 0.5, 0.75, 1; U = 530V
    eta_max = [0, 0.95, 0.96, 0.962, 0.961, 0.9524]  # P/P_max = 0, 0.2, 0.3, 0.5, 0.75, 1; U = 560V
    # dc voltage at min, nom and max
    dc_voltage = [[175.], [530.], [560.]]
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
    Import the Inverter SMA SUNNY BOY 3000HF to pvlib

    :return:
    inverter dictionary, type: sandia model
    """
    # inverter efficiency at different power points
    eta_min = [0, 0.945, 0.95, 0.947, 0.942, 0.931]  # P/P_max = 0, 0.2, 0.3, 0.5, 0.75, 1; U = 210V
    eta_nom = [0, 0.953, 0.962, 0.963, 0.96, 0.952]  # P/P_max = 0, 0.2, 0.3, 0.5, 0.75, 1; U = 530V
    eta_max = [0, 0.95, 0.96, 0.962, 0.961, 0.9524]  # P/P_max = 0, 0.2, 0.3, 0.5, 0.75, 1; U = 560V
    # dc voltage at min, nom and max
    dc_voltage = [[175.], [530.], [560.]]
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
        "p_ac_0": 3000.,
        "p_nt": 1.
    }

    # call method that creates sandia inverter model
    inverter = pvlib.inverter.fit_sandia(sma_sb_data["ac_power"], sma_sb_data["dc_power"], sma_sb_data["dc_voltage"],
                                         sma_sb_data["dc_voltage_level"], sma_sb_data["p_ac_0"], sma_sb_data["p_nt"])
    return inverter


if __name__ == "__main__":
    inv = get_sma_sb_3000hf()
    print(inv)
