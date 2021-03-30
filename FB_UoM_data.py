import pickle
import pandas as pd, numpy as np
from datetime import *

here = '/home/tobin/COVID-Risk-App'
here = '/Users/tobin/Dropbox/MPhil/Projects/COVID Risk Mapping/Bandicoot Code'


######################################################################################################################################################################
# Loading in Facebook Data
######################################################################################################################################################################

fake_data = pd.read_csv(here+'/data/FB_sample_data.csv')
fake = True  # Use when debugging avoid calling the server constantly.

import pyodbc, json
with open(here+'/server_credentials.json', 'r') as f:
	creds = json.load(f)

def get_fb_data(time, region, start_date, end_date):
	"""Collects Origin-Destination flow dataframe from UMelb SQL server.

    Extended description of function.

    Args:
        date (str): Date string in '%Y-%M-%d' (e.g. "2021-01-01")
        time (str): Choice of time slice between 0000, 0600, 1200 and *. 
		region (str): Abbreviation of state (e.g. "SA" or "VIC")

    Returns:
        pandas.DataFrame: A dataframe of origin-destination flows in a long format. 
			Columns are LGA19_source, LGA19_target and n_trips.
    """

	if fake:  # Use when debugging avoid calling the server constantly.
		print('Getting fake data')
		date = datetime.strptime(start_date, '%Y-%M-%d').strftime('%-d/%-M/%y')
		grouped = fake_data.groupby(['date','time', 'region'])
		ODflows = grouped.get_group((date, time, region))
		return ODflows
	else:
		with pyodbc.connect('DRIVER='+creds["driver"]+';SERVER='+creds["server"]+';DATABASE='+creds["database"]+';UID='+creds["username"]+';PWD='+ creds["password"]) as conn:
			query = "SELECT * FROM dbo.FB_LGA19_OD WHERE date>='%s' AND date<='%s' AND region = '%s' AND time=%s" % (
				start_date, end_date, region, time)
			response_dataframe = pd.read_sql_query(query, conn)
			# print('Query from database: ', start_date, end_date,  time, region, '; Result length = ', len(response_dataframe))
			response_dataframe = response_dataframe[~response_dataframe.duplicated()]
			response_dataframe.LGA19_source = pd.to_numeric(response_dataframe.LGA19_source)
			response_dataframe.LGA19_target = pd.to_numeric(response_dataframe.LGA19_target)
			response_dataframe['time'] = pd.to_numeric(response_dataframe['time'])
			# response_dataframe['region'] = pd.to_numeric(response_dataframe['region'])
			response_dataframe = response_dataframe.groupby(
				['LGA19_source', 'LGA19_target', 'region']).sum().reset_index()

	return response_dataframe

######################################################################################################################################################################
# Calculating Risk
######################################################################################################################################################################

def get_fb_risk(ODflows, locations, state):
	"""The function used to calculate risk based on the origin destination matrix of flows.

    Args:
        ODflows (pandas.Dataframe): An origin-destination dataframe with counts of individuals moving from one LGA region to another. 
        locations (list): A list of LGA locations (as int's) that the outbreak simulation should be started from.
		state (int): A value [0,7] that can be used to specify what state is being examined.

    Returns:
        dict: A dictionary of { LGA code : risk estimate } pairs which will be plotted.

    """
	# print('Risk locations:', locations)

	# Keep only flows that are within state
	ODflows = ODflows[(ODflows.LGA19_source // 10000 == state)  & (ODflows.LGA19_target // 10000 == state)]
	
	# Convert to wide format matrix
	ODmatrix = ODflows.pivot(values = 'n_trips', columns = 'LGA19_target', index ='LGA19_source')

	# Make sure the index is matched
	ODmatrix = ODmatrix.reindex(sorted(ODmatrix.columns), axis=1)
	ODmatrix = ODmatrix.sort_index()

	# Set non-flow edges to 0
	ODmatrix = ODmatrix.fillna(0) 

	# Option set diagonal to 0 
	# np.fill_diagonal(ODmatrix.values, 0)

	if len(locations) == 0:
		risk_vector = ODmatrix.sum(axis=0)
		risk_vector = risk_vector / risk_vector.sum()
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
	1 : {"lat": -33.8708, "lon": 151.2073},
	2 : {"lat": -37.8136, "lon": 144.9631},
	3 : {"lat": -27.4698, "lon": 153.0251},
	4 : {"lat": -34.9285, "lon": 138.6007},
	5 : {"lat": -31.9505, "lon": 115.8605},
	6 : {"lat": -42.8821, "lon": 147.3272},
	7 : {"lat": -12.4634, "lon": 130.8456}
}

# Useful maps of information
state_fullname_map = {1: 'New South Wales', 2: 'Victoria', 3: 'Queensland', 4: 'South Australia', 5: 'Western Australia',
                      6: 'Tasmania', 7: 'Northern Territory'}
state_acronym_map = {4: 'SA', 7: 'NT', 3: 'QLD',
                     5: 'WA', 1: 'NSW', 2: 'VIC', 6: 'TAS'}

# Loading in a dictionary of LGA Codes to Proper Names
with open(here+"/data/lga_name_map.pickle", "rb") as f:
	lga_name_map = pickle.load(f)


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
                "text": "Loading...",
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
