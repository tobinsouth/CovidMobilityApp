import pandas as pd
import numpy as np
import geopandas
from .params import here


# Helpful variables
import json
with open(here+'/data/LGA_mapping.json','r') as f:
    LGA_mapping = json.load(f)
    LGA_mapping['Australian Capital Territory'] = {}

# Update Choropleth
full_geo_df = geopandas.read_file(here+"/data/LGA_shapefile.geojson")
full_geo_df.id = pd.to_numeric(full_geo_df.id)
full_geo_df.LGA_CODE19 = pd.to_numeric(full_geo_df.LGA_CODE19)
full_geo_df.AREASQKM19 = pd.to_numeric(full_geo_df.AREASQKM19)
full_geo_df.STE_CODE16 = pd.to_numeric(full_geo_df.STE_CODE16)
full_geo_df = full_geo_df.set_index('id')

# Latitudes and longitudes of major state capitals
cbd_lat_longs = {
	'New South Wales' : {"lat": -33.8708, "lon": 151.2073},
	'Victoria' : {"lat": -37.8136, "lon": 144.9631},
	'Queensland' : {"lat": -27.4698, "lon": 153.0251},
	'South Australia' : {"lat": -34.9285, "lon": 138.6007},
	'Western Australia' : {"lat": -31.9505, "lon": 115.8605},
	'Tasmania' : {"lat": -42.8821, "lon": 147.3272},
	'Northern Territory' : {"lat": -12.4634, "lon": 130.8456}
}

states = ['New South Wales',
       'Northern Territory', 'Queensland', 'South Australia', 'Tasmania',
       'Victoria', 'Western Australia']

variables_to_plot = ['retail_and_recreation_percent_change_from_baseline',
       'grocery_and_pharmacy_percent_change_from_baseline',
       'parks_percent_change_from_baseline',
       'transit_stations_percent_change_from_baseline',
       'workplaces_percent_change_from_baseline',
       'residential_percent_change_from_baseline']

nice_variable_names = {
    'retail_and_recreation_percent_change_from_baseline':"Retail and recreation",
    'grocery_and_pharmacy_percent_change_from_baseline':"Supermarket and pharmacy",
    'parks_percent_change_from_baseline':"Parks",
    'transit_stations_percent_change_from_baseline':"Public transport",
    'workplaces_percent_change_from_baseline':"Workplaces",
    'residential_percent_change_from_baseline':"Residential",
}


explainer_variable_mapping = {
    'retail_and_recreation_percent_change_from_baseline':"Mobility trends for places such as restaurants, cafés, shopping centres, theme parks, museums, libraries and cinemas.",
    'grocery_and_pharmacy_percent_change_from_baseline':"Mobility trends for places such as supermarkets, food warehouses, farmers markets, specialty food shops and pharmacies.",
    'parks_percent_change_from_baseline':"Mobility trends for places like national parks, public beaches, marinas, dog parks, plazas and public gardens.",
    'transit_stations_percent_change_from_baseline':"Mobility trends for places that are public transport hubs, such as underground, bus and train stations.",
    'workplaces_percent_change_from_baseline':"Mobility trends for places of work.",
    'residential_percent_change_from_baseline':"Mobility trends for places of residence.",
}



# Load in google data
def update_google_data():
    """ Read in global CSV (this one isn't zipped) from the google site"""
    google = pd.read_csv('https://www.gstatic.com/covid19/mobility/Global_Mobility_Report.csv',parse_dates=['date']).query("country_region_code=='AU'")
    google.rename({'sub_region_1':'state', 'sub_region_2':'Council'}, axis=1, inplace=True) # For clarity
    google = google[['country_region_code', 'country_region', 'state', 'Council', 'date']+variables_to_plot]
    google['LGA'] = [LGA_mapping.get(state, {}).get(LGA, np.NaN) for state, LGA in zip(google['state'], google['Council'])]
    google.to_csv(here+'/data/google_mobility_australia.csv', index=False)
    with open(here+'/data/google_data.txt','w') as f: 
        f.write(pd.to_datetime('today').strftime('%Y-%m-%d'))



with open(here+'/data/google_data.txt','r') as f: 
    collected_date = f.read()
if collected_date != pd.to_datetime('today').strftime('%Y-%m-%d'):
    update_google_data()

google = pd.read_csv(here+'/data/google_mobility_australia.csv',parse_dates=['date'])
google = google[~google.state.isna()] # Remove Australia wide data
latest_date = max(google.date) # Get the latest google data in the data


# An empty figure object to show when there is no data
empty_graph = {
    "layout": {
        "xaxis": {
            "visible": False
        },
        "yaxis": {
            "visible": False
        },
        "annotations": [
            {
                "text": "Waiting for risk estimate...",
                "xref": "paper",
                "yref": "paper",
                "showarrow": False,
                "font": {
                    "size": 20
                }
            }
        ]
    }
}

instruction_graph = {
    "layout": {
        "xaxis": {
            "visible": False
        },
        "yaxis": {
            "visible": False
        },
        "annotations": [
            {
                "text": "Click on a local government area on the left",
                "xref": "paper",
                "yref": "paper",
                "showarrow": False,
                "font": {
                    "size": 20
                }
            }
        ]
    }
}