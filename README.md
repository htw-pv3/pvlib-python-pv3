# PV3 - SonnJA pvlib model

<a href="https://github.com/htw-pv3"><img align="right" width="100" height="100" src="https://avatars.githubusercontent.com/u/64144501?s=200&v=4" alt="PV3"></a>

## License / Copyright

This repository is licensed under [BSD 3-Clause License (BSD-3-Clause)](https://www.gnu.org/licenses/agpl-3.0.en.html)

## Installation

### Setup environment

`conda env create -f requirements.yml` <br>
`activate d_py38_pv3`

### required packages for this REPO

csv, colorlover, getpass, glob, IPython.display, json, matplotlib, plotly, pylab, os, pandas, scipy, scipy.interpolate,seaborn, sqalchemy, sys

### How to start and execute the pvlib

Start:

- open cmd and activate your env -> conda activate d_py37_vis
- open pgAdmin and log in to database "sonnJA"
- open git bash in D:\git\github\htw-pv3\pvlib-python-pv3
- update your repository! -> git pull
- open PyCharm and open project "pvlib"

Your pvlib is now setup and you are ready to run or work in the pvlib! (make sure to create a local branch for changes)

Execute:

- if you want to create new export files, make sure to remove the "#" at the start of each "Export Data" line in pv3_main.py
- run pv3_main
- PyCharm will ask you for the password of the database -> type it in and the pvlib will continue
- new csv- and dat-files will be created and added to D:\git\github\htw-pv3\pvlib-python-pv3\data

### Setup folder and data

Create a folder _data_ and _data/pv3_2015_
Run SQL scripts to create and fill database with weather data: https://github.com/htw-pv3/weather-data/tree/master/postgresql

Note: The data used is not provided due to licensing issues. <br>
Please contact @Ludee for further information.

### Database of pvlib

To find solar modules or inverter in the database of pvlib open pv3_pvlib_sam_data.ipynb in jupyter notebook.
In this file you will find an examples of the existing database's and which components are included. Furthermore the electrical specification

## Research object

The test object is the PV system SonnJA!, which was planned by students of the HTW Berlin and the organization einleuchtend e.V..
It was planned in between 2010 and 2013 and is placed on about 620 m^2 of the roof area of the building G of the Wilheminenhof campus. 
The produced electricity of this 16 kWp power plant is fed into one phase of the university internal grid of HTW Berlin and remunerated according to the EEG. 
The special quality of this PV system is its conception as a research system: the system has three different module technologies, two types of inverters and a comprehensive monitoring system with its own weather station. 
