# pvlib-python-pv3
Create a python model using the pvlib

## Install

### Setup environment

conda env create -f requirements.yml
activate d_py37_pv

#### How to start and execute the pvlib

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


