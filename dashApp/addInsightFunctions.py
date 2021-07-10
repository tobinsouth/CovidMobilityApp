#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import AddInsights functions
from .addInsights.Addinsight import *
from .addInsights.Group import * 
from .addInsights.ODTripsByGroup import *
import geopandas
import numpy as np

from .params import here


# Helper functions
import json
with open(here+'/data/addInsights_credentials.json.json', 'r') as f:
	creds = json.load(f)

def connectionSetup():
    """Establish API Connection"""
    api_token = creds['api_token']
    addinsight_url_base = creds['addinsight_url_base']
    print('Connecting to client')
    return Addinsight(api_token, addinsight_url_base, 2, 10)


def retrieveGroupDefinitions(ai_connection):
    """Define Groups definition request"""
    groupExpandProperties = ['included_objects','coordinates']
    groupCategoryNameFilter = 'ABS SA2 Boundaries'
    groups = GroupRequest(ai_connection, groupExpandProperties, groupCategoryNameFilter)
    groupIds = groups.getGroupIds()
    print('Group data collected.')
    return groups, groupIds



def getODbySA2(start_date, end_date, start_time_of_day, end_time_of_day, ai_connection, groupIdsSymmetrical):
    """
    Collects OD trips for given timespan.

    Will collected the total number of Origin-Destination (OD) trips between each possible 
    pair of groups (given by AddInsights groupIds) over the between start_time_of_day and 
    end_time_of_day for each day between start_date and end_date inclusive. 
    Data is aggregated over this whole period.

    Args:
        start_date (str): A start date string e.g. "2020-01-01"
        end_date (str): A end date string e.g. "2020-01-01"
        start_time_of_day (str): A time string e.g. "01:45"
        end_time_of_day (str): A time string e.g. "23:45"

    Returns:
        pandas.DataFrame: A long format dataframe of each OD pair and the total number of trips.

    """
    days_of_week = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday' ]
    exclude_special_day_type_ids = []
    include_special_day_type_ids = []
    source_id_types = [ 'bt' ]
    aggregate = 'entire_range' 
    aggregate_merge = None
    odTripsByGroup = ODTripsByGroupReport(ai_connection, start_date, end_date, start_time_of_day, end_time_of_day, days_of_week,
        exclude_special_day_type_ids, include_special_day_type_ids, aggregate, aggregate_merge, 
        groupIdsSymmetrical, groupIdsSymmetrical, source_id_types)

    flow_data_long = odTripsByGroup.createFlowList()
    flow_data_long.drop('intervalTime', axis = 1, inplace = True)
    # flow_data_long.to_csv('data/lastest_addinsights.csv', index = False)
    return flow_data_long

sa2_name_map = {'Adelaide': 2, 'North Adelaide': 3, 'Aldgate Stirling': 4, 'Mount Barker': 5, 'Burnside Wattle Park': 6, 'Glenside Beaumont': 7, 'Toorak Gardens': 8, 'Paradise Newton': 9, 'Rostrevor Magill': 10, 'Norwood (SA)': 11, 'Payneham Felixstow': 12, 'St Peters Marden': 13, 'Nailsworth Broadview': 14, 'Prospect': 15, 'Walkerville': 16, 'Goodwood Millswood': 17, 'Unley Parkside': 18, 'Gawler North': 19, 'Gawler South': 20, 'Elizabeth': 21, 'Munno Para West Angle Vale': 22, 'Smithfield Elizabeth North': 23, 'Virginia Waterloo Corner': 24, 'Enfield Blair Athol': 25, 'Northgate Oakden Gilles Plains': 26, 'Windsor Gardens': 27, 'Dry Creek North': 28, 'Ingle Farm': 29, 'Para Hills': 30, 'Parafield': 31, 'Parafield Gardens': 32, 'Paralowie': 33, 'Salisbury': 34, 'Salisbury East': 35, 'Mawson Lakes Globe Derby Park': 36, 'Pooraka Cavan': 37, 'Golden Grove': 38, 'Greenwith': 39, 'Highbury Dernancourt': 40, 'Hope Valley Modbury': 41, 'Modbury Heights': 42, 'St Agnes Ridgehaven': 43, 'Brighton (SA)': 44, 'Glenelg (SA)': 45, 'Edwardstown': 46, 'Hallett Cove': 47, 'Marino Seaview Downs': 48, 'Mitchell Park': 49, 'Morphettville': 50, 'Sheidow Park Trott Park': 51, 'Warradale': 52, 'Belair': 53, 'Bellevue Heights': 54, 'Blackwood': 55, 'Colonel Light Gardens': 56, 'Mitcham (SA)': 57, 'Panorama': 58, 'Aldinga': 59, 'Christie Downs': 60, 'Christies Beach': 61, 'Flagstaff Hill': 62, 'Hackham Onkaparinga Hills': 63, 'Hackham West Huntfield Heights': 64, 'Happy Valley Reservoir': 65, 'Lonsdale': 66, 'McLaren Vale': 67, 'Morphett Vale East': 68, 'Morphett Vale West': 69, 'Reynella': 70, 'Seaford (SA)': 71, 'Woodcroft': 72, 'Beverley': 73, 'Flinders Park': 74, 'Henley Beach': 75, 'Hindmarsh Brompton': 76, 'Royal Park Hendon Albert Park': 77, 'Seaton Grange': 78, 'West Lakes': 79, 'Woodville Cheltenham': 80, 'Dry Creek South': 81, 'Largs Bay Semaphore': 82, 'North Haven': 83, 'Port Adelaide': 84, 'The Parks': 85, 'Adelaide Airport': 86, 'Fulham': 87, 'Lockleys': 88, 'Plympton': 89, 'Richmond (SA)': 90, 'West Beach': 91, 'Nuriootpa': 92, 'Wakefield Barunga West': 93, 'Whyalla': 94, 'Whyalla North': 95, 'Port Augusta': 96, 'Mount Gambier East': 97, 'Mount Gambier West': 98, 'Murray Bridge': 99, 'Hahndorf Echunga': 121, 'Lobethal Woodside': 122, 'Mount Barker Region': 123, 'Nairne': 124, 'Goolwa Port Elliot': 125, 'Strathalbyn': 126, 'Yankalilla': 127, 'Murray Bridge Region': 128}

def get_risk(flow_data_long, locations):
    
    print('Locations:', locations)
    # Convert to wide format matrix
    ODmatrix = flow_data_long.pivot(values = 'value', columns = 'destGroupId', index ='originGroupId')

    # Make sure the index is matched
    ODmatrix = ODmatrix.reindex(sorted(ODmatrix.columns), axis=1)
    ODmatrix = ODmatrix.sort_index()

    # Set non-flow edges to 0
    ODmatrix = ODmatrix.fillna(0) 

    # Set self-flows to 0
    # np.fill_diagonal(wide_format.values, 0) #?

    if len(locations) == 0:
        risk_vector = ODmatrix.sum(axis=0)
        risk_vector = risk_vector / risk_vector.sum() # Normalise risk vector
        risk_vector = dict(zip(ODmatrix.index, risk_vector))
    else:
        p = np.array([1 if loc in locations else 0 for loc in ODmatrix.index])  # Prevalence vector
        risk_vector = np.matmul(ODmatrix.to_numpy(), p)
        risk_vector = risk_vector / risk_vector.sum() # Normalise risk vector
        risk_vector = dict(zip(ODmatrix.index, risk_vector))

    return risk_vector


######################################################################################################################################################################
# Helpful Variables
######################################################################################################################################################################

# Latitudes and longitudes of major state capitals
cbd_lat_longs = {
	# 1 : {"lat": -33.8708, "lon": 151.2073},
	# 2 : {"lat": -37.8136, "lon": 144.9631},
	# 3 : {"lat": -27.4698, "lon": 153.0251},
	4 : {"lat": -34.9285, "lon": 138.6007},
	# 5 : {"lat": -31.9505, "lon": 115.8605},
	# 6 : {"lat": -42.8821, "lon": 147.3272},
	# 7 : {"lat": -12.4634, "lon": 130.8456}
}



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

# Update Choropleth
# print('Reading in geopandas')
full_geo_df = geopandas.read_file(here+"/data/SA2GeoJson.gjson")
groupIds =  list(full_geo_df.id)
full_geo_df = full_geo_df.set_index('id')

ai_connection = connectionSetup() # Connection client

all_sa2_names = full_geo_df['normalname'].to_dict()

state = 4


