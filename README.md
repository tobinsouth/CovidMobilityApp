# COVID-19 Spatial Risk Mapping using Facebook Data
COVID-19 is highly transmissible and containing outbreaks requires a rapid and effective response. Because infection may be spread by people who are pre-symptomatic or asymptomatic, substantial undetected transmission is likely to occur before clinical cases are diagnosed. When outbreaks occur there is a need to anticipate which populations and locations are at heightened risk of exposure.

This app uses aggregate human mobility data for estimating the geographical distribution of transmission risk. This aggregate data is provided by [Facebook's Data for Good initiative](https://dataforgood.fb.com/). To learn more about the methods used here, their reliability and their applicability, read [Risk mapping for COVID-19 outbreaks in Australia using mobility data](https://royalsocietypublishing.org/doi/full/10.1098/rsif.2020.0657).


## Technical information
This repository contains the front end of the visualization. It uses Dash to map FB movement data across Local Government Areas (LGA). Movement aggregations from Facebooks tiles are done at the Univerity of Melbourne. 
  
To run you will need a `server_credentials.json` file with the access credidtials to the UMelb database. This should come in the format:
`{"server": "<name>.database.windows.net", "database": "<db_name>", "username": "<username>", "password": "<pwd>", "driver": "{ODBC Driver 17 for SQL Server}"}`

To run on an Apache server with WSGI:
- Put the `wsgi_files/dash.conf` file in `/etc/apache2/sites-available` on your server.
- Put the `wsgi_files/coviddash.wsgi` file in `/var/www/html/wsgi/`.






Shield: [![CC BY-NC-SA 4.0][cc-by-nc-sa-shield]][cc-by-nc-sa]

This work is licensed under a
[Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License][cc-by-nc-sa].

[![CC BY-NC-SA 4.0][cc-by-nc-sa-image]][cc-by-nc-sa]