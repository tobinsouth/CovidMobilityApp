print('Downloading Google data')
import pandas as pd, numpy as np

variables_to_plot = ['retail_and_recreation_percent_change_from_baseline',
       'grocery_and_pharmacy_percent_change_from_baseline',
       'parks_percent_change_from_baseline',
       'transit_stations_percent_change_from_baseline',
       'workplaces_percent_change_from_baseline',
       'residential_percent_change_from_baseline']
       
import json
with open('./dashApp/data/LGA_mapping.json','r') as f:
    LGA_mapping = json.load(f)
    LGA_mapping['Australian Capital Territory'] = {}

google = pd.read_csv('https://www.gstatic.com/covid19/mobility/Global_Mobility_Report.csv',parse_dates=['date'])
google = google.query("country_region_code=='AU'")
google.rename({'sub_region_1':'state', 'sub_region_2':'Council'}, axis=1, inplace=True) # For clarity
google = google[['country_region_code', 'country_region', 'state', 'Council', 'date']+variables_to_plot]
google['LGA'] = [LGA_mapping.get(state, {}).get(LGA, np.NaN) for state, LGA in zip(google['state'], google['Council'])]
google.to_csv('./dashApp/data/google_mobility_australia.csv', index=False)
with open('./dashApp/data/google_data.txt','w') as f: 
    f.write(pd.to_datetime('today').strftime('%Y-%m-%d'))

