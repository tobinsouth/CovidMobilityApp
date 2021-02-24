import pickle
import pandas as pd, numpy as np
from datetime import *

######################################################################################################################################################################
# Loading in Facebook Data
######################################################################################################################################################################

fake_data = pd.read_csv('data/FB_sample_data.csv')
fake = False  # Use when debugging avoid calling the server constantly.

import pyodbc, json
with open('server_credentials.json', 'r') as f:
	creds = json.load(f)

def get_fb_data(date, time, region):
	if fake:  # Use when debugging avoid calling the server constantly.
		print('Getting fake data')
		date = datetime.strptime(date, '%Y-%M-%d').strftime('%-d/%-M/%y')
		grouped = fake_data.groupby(['date','time', 'region'])
		ODflows = grouped.get_group((date, time, region))
		return ODflows
	else:
		with pyodbc.connect('DRIVER='+creds["driver"]+';SERVER='+creds["server"]+';DATABASE='+creds["database"]+';UID='+creds["username"]+';PWD='+ creds["password"]) as conn:
			query = "SELECT * FROM dbo.FB_LGA19_OD WHERE date='%s' AND region = '%s' AND time=%04d" % (date, region, time)
			response_dataframe = pd.read_sql_query(query, conn)
			print('Query from database: ', date, time, region, '; Result length = ', len(response_dataframe))
			response_dataframe = response_dataframe[~response_dataframe.duplicated()]
		return response_dataframe

######################################################################################################################################################################
# Calculating Risk
######################################################################################################################################################################

def get_fb_risk(ODflows, locations, state):
	print('Risk locations:', locations)

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
	np.fill_diagonal(ODmatrix.values, 0)

	if len(locations) == 0:
		risk_vector = ODmatrix.sum(axis=0)
		risk_vector = risk_vector / risk_vector.sum()
		risk_vector = dict(zip(ODmatrix.index, risk_vector))
	elif len(locations) == 1:
		# Normalise by row sums
		ODmatrix = ODmatrix.div(ODmatrix.sum(axis=1), axis=0)
		risk_vector = ODmatrix.iloc[locations[0], :]
		risk_vector = risk_vector / risk_vector.sum()
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
                      6: 'Tasmania', 7: 'Northern Territory', 8: 'Australian Capital Territory', 9: 'Other Territories'}
state_acronym_map = {4: 'SA', 7: 'NT', 3: 'QLD',
                     5: 'WA', 1: 'NSW', 2: 'VIC', 6: 'TAS'}

# Loading in a dictionary of LGA Codes to Proper Names
with open("data/lga_name_map.pickle", "rb") as f:
	lga_name_map = pickle.load(f)
