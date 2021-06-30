import pvlib
import numpy as np


sma_sb_data = {
    "ac_power": np.array([750., 2271, 3000]),  # Annahme: Strom bleibt in allen Punkten gleich
    "dc_power": np.array([788., 2385, 3150]),  # Annahme: Strom bleibt in allen Punkten gleich
    "dc_voltage": np.array([175, 530, 700]),
    "dc_voltage_level": np.array(["Vmin", "Vnom", "Vmax"]),
    "p_ac_0": 3150.,
    "p_nt": 1.
}

sma_sb_3000_hf = pvlib.inverter.fit_sandia(sma_sb_data["ac_power"], sma_sb_data["dc_power"], sma_sb_data["dc_voltage"],
                                           sma_sb_data["dc_voltage_level"], sma_sb_data["p_ac_0"], sma_sb_data["p_nt"])
print(sma_sb_3000_hf)
