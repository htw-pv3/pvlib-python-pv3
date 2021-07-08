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



The test object is the PV system SonnJA!, which was planned by students of the HTW Berlin and the organization einleuchtend e.V..
It was planned in between 2010 and 2013 and is placed on about 620 m^2 of the roof area of the building G of the Wilheminenhof campus. 
The produced electricity of this 16 kWp power plant is fed into one phase of the university internal grid of HTW Berlin and remunerated according to the EEG. 
The special quality of this PV system is its conception as a research system: the system has three different module technologies, two types of inverters and a comprehensive monitoring system with its own weather station. 
