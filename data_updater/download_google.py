print('Downloading Google data')
import pandas as pd

variables_to_plot = ['retail_and_recreation_percent_change_from_baseline',
       'grocery_and_pharmacy_percent_change_from_baseline',
       'parks_percent_change_from_baseline',
       'transit_stations_percent_change_from_baseline',
       'workplaces_percent_change_from_baseline',
       'residential_percent_change_from_baseline']
       

google = pd.read_csv('https://www.gstatic.com/covid19/mobility/Global_Mobility_Report.csv',parse_dates=['date'])
google = google.query("country_region_code=='AU'")
google.rename({'sub_region_1':'state', 'sub_region_2':'Council'}, axis=1, inplace=True) # For clarity
google = google[['country_region_code', 'country_region', 'state', 'Council', 'date']+variables_to_plot]
google.to_csv('dashApp/data/google_mobility_australia.csv', index=False)


