# PV3 - SonnJA pvlib model

<a href="https://github.com/htw-pv3"><img align="right" width="100" height="100" src="https://avatars.githubusercontent.com/u/64144501?s=200&v=4" alt="PV3"></a>

## License / Copyright

This repository is licensed under [BSD 3-Clause License (BSD-3-Clause)](https://www.gnu.org/licenses/agpl-3.0.en.html)

## Installation

### Setup environment

`conda env create -f requirements.yml` <br>
`activate d_py38_pv3`

### Setup folder and data

Create a folder _data_ and _data/pv3_2015_
Run SQL scripts to create and fill database with weather data: https://github.com/htw-pv3/weather-data/tree/master/postgresql

Note: The data used is not provided due to licensing issues. <br>
Please contact @Ludee for further information.

### Database of pvlib

To find solar modules or inverter in the database of pvlib open pv3_pvlib_sam_data.ipynb in jupyter notebook.
In this file you will find an examples of the existing database's and which components are included. Furthermore the electrical specification


