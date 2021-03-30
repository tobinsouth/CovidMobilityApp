#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import Dash components
import dash
import dash_core_components as dcc
import dash_html_components as html
from textwrap import dedent as d # For writing markdown text
import plotly.graph_objs as go
import plotly.express as px
import json
from dash.dependencies import Output, Input, State
from datetime import *

# For downloading csv
from dash_extensions import Download
from dash_extensions.snippets import send_data_frame

# Import FB UoM Data Collection
from FB_UoM_data import *

import logging, sys, os
# logging.basicConfig(filename=here+'/temp/python.log', level=logging.INFO, 
#                     format='%(asctime)s %(levelname)s %(name)s %(message)s')
# # os.chmod(LOG_FILENAME, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO);
# logging.info('Server should be starting.')
# logging.info('Python version and path' + sys.version)
# # for p in sys.path:
# #     logging.info(p)
# os.chmod(here+'/temp/python.log', 0o777)

print('Server should be starting')
######################################################################################################################################################################
# This is the setup of the actual dash html interface
######################################################################################################################################################################

# import the css template, and pass the css template into dash
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets,
                requests_pathname_prefix='/coviddash/' )  # requests_pathname_prefix='/coviddash/',
app.title = "COVID-19 Risk Map"

# styles: for right side hover/click component
styles = {
	'pre': {
		'border': 'thin lightgrey solid',
		'overflowX': 'scroll'
	}
}

app.layout = html.Div([
	# Title & Explainer
	html.Div([html.H1("COVID-19 Risk Mapping")], className="row",  style={'textAlign': "center"}),
	html.Div(className="row", style={'textAlign': "justify", 'padding-right': '30px', 'padding-left': '30px'},
		children = dcc.Markdown(d(
		"""
		COVID-19 is highly transmissible and containing outbreaks requires a rapid and effective response. Because infection may be spread by people who are pre-symptomatic or asymptomatic, substantial undetected transmission is likely to occur before clinical cases are diagnosed. When outbreaks occur there is a need to anticipate which populations and locations are at heightened risk of exposure.

		This app uses aggregate human mobility data for estimating the geographical distribution of transmission risk. This aggregate data is provided by [Facebook's Data for Good](https://dataforgood.fb.com/) initiative. To learn more about the methods used here, their reliability and their applicability, read [Risk mapping for COVID-19 outbreaks in Australia using mobility data](https://royalsocietypublishing.org/doi/full/10.1098/rsif.2020.0657).

		To use the app select a range of dates and times to aggregate mobility data over for a state. Outbreaks may be started from any set of local government areas. A generalised risk profile will be generated when no locations are selected.
		"""
		))),
	html.Hr(),
	# Input selectors
	html.Div(
		className="row border border-secondary", style={'textAlign': "center"}, 
		children=[
			# Date picker
			html.Div(
				className="three columns", 
				children=[
					dcc.Markdown(d("""
						#### Select Dates
						""")),
					dcc.DatePickerRange(
                        id='date_picker',
                        min_date_allowed=date(2020, 5, 1),
                        max_date_allowed=date.today(),
                        start_date = date(2021, 1, 1),
                        end_date= date(2021, 1, 10)
                    ),
					# dcc.DatePickerSingle(
					# 	id='date_picker',
					# 	min_date_allowed=date(2020, 5, 1),
					# 	max_date_allowed=date.today(),
					# 	date = date(2021, 1, 1),
					# ),
				]
			),
			# Time picker
			html.Div(
				className="two columns",
				children=[
					dcc.Markdown(d("""
						#### Select Times
						""")),
					dcc.Dropdown(
						id = 'time_option',
						options=[
							{'label': 'Morning', 'value': '0000'},
							{'label': 'Afternoon', 'value': '0800'},
							{'label': 'Night', 'value': '1600'},
							{'label': 'All', 'value': '*'}
						],
						value=0,
						searchable=False
						# labelStyle={'display': 'inline-block'}
					),
				]
			),
			# State picker
			html.Div(
				className="three columns",
				children=[
					dcc.Markdown(d("""
						#### Select State
						""")),
					dcc.Dropdown(
						id = 'state',
						options= [ {'label':v, 'value':k} for k,v in state_fullname_map.items()],
						value=1,
						searchable=False
						# labelStyle={'display': 'inline-block'}
					),
				]
			),
			# Location picker
			html.Div(
				className="four columns",
				children=[
					dcc.Markdown(d("""
						#### Outbreak Centres
						""")),
					dcc.Dropdown(
						id='locations',
						options= [ {'label':v, 'value':k} for k,v in lga_name_map.items() if k // 10000 == 1],
						value= [],
						multi=True
					),
					# dcc.Checklist(id='select-all-from-dropdown',
					# 	options=[{'label': 'Select All', 'value': 1}], value=[]),
					# html.Div(id='show-locations'),
				]
			)
		]
	),
	html.Div(className="row"),
	dcc.Markdown(d("""
			After selecting the desired inputs, click the Create Risk Estimate button to begin calculation. This may take several seconds to process and display depending on your hardware.
		"""), style={'textAlign': "center", "margin-top": "15px"}),
	html.Hr(),
	# Submit button
	dcc.Loading(
            id="loading-bar",
            type="default",
			children=[
				html.Div(
					className="row",  style={'textAlign': "center"}, 
					children=[
						html.Button("Create Risk Estimate", id="submit_button")
						]
				),
				# Hidden div inside the app that stores the risk values
				html.Div(id='risk_estimate_variable', style={'display': 'none'}),
				html.Div(id="loading-output")
			]
	),
	html.Hr(),
	# Plots 
	dcc.Loading(
            id="loading-bar-figures",
            type="default",
			children=[
				html.Div(
					className="row",
					children=[            
						html.Div(
							className="eight columns",
							children=[
								dcc.Markdown(d("""
									### Risk Map:
									""")),
								dcc.Graph(id="choropleth", figure=empty_graph)
							]
						),
						html.Div(
							className="four columns",
							children=[
								dcc.Markdown(d("""
									### Highest Risk Areas:
									""")),
								dcc.Graph(id='high_risk_areas', figure=empty_graph)
							]

						),
					]
				),
			]
	),
	html.Hr(),
	html.Div(
		className="row",  style={'textAlign': "center"}, 
		children=[
			html.Button("Download Risk Potential as CSV", id="download_button")
			]
	),
	# Element to allow for file download
	Download(id="download_div"),
	html.Hr(),
	html.Div(
		className="row",  style={'textAlign': "justify", 'padding-right': '30px', 'padding-left': '30px'},
		children=dcc.Markdown(d(
			"""
			Research associated with this app has demonstrated that mobility data can be a good predictor of geographical patterns of exposure risk from transmission centres, particularly in outbreaks involving workplaces or other environments associated with habitual travel patterns [[1]](https://royalsocietypublishing.org/doi/full/10.1098/rsif.2020.0657). Mobility data add the most value to risk predictions when case counts are low and spatially clustered and can assist health systems in the allocation of testing resources, and potentially guide the implementation of geographically targeted restrictions on movement and social interaction.

			#### Disclaimer 

			The organsiations that authored this app accept no responsibility for the results of any actions taken on the basis of information on this website, nor for the accuracy or completeness of any material contained herein. 
			
			Please note this app may discontinue or vary at any time without notice.

			This website contains links to external organisations and information. The organsiations that authored this app accept do not accept responsibility for, nor endorse, the content of any linked site.
			"""
			))),

])

######################################################################################################################################################################
# These callbacks are what will make everything interactive
######################################################################################################################################################################

# # Show selected locations
# @app.callback(Output('show-locations', 'children'), Input('locations', 'value'), State('select-all-from-dropdown', 'value'))
# def display_locations(values, all_option):
# 	if len(values)==0:
# 		return None #"No locations selected, will show generalized risk estimate."
# 	if all_option != []:
# 		if all_option[0] == 1:
# 			return "All possible locations selected, which is pretty much the same thing as selecting no locations."
# 	return None # "Selected %d locations. Risk map will be estimated starting from these locations." % len(values)
# 	# return ", ".join(values)


# # Select all possible starting locations.
# @app.callback( Output('locations', 'value'),
# 	[Input('select-all-from-dropdown', 'value')],
# 	[State('locations', 'options'),
# 	 State('locations', 'value')])
# def select_all_locations(selected, options, values):
# 	if selected != []:
# 		if selected[0] == 1:
# 			return [i['value'] for i in options]
# 	return values

# Update location list according to state
@app.callback(Output('locations', 'options'),
              [Input('state', 'value')])
def update_possible_state_locations(state):
	return [{'label': v, 'value': k} for k, v in lga_name_map.items() if k // 10000 == state]


# Get new data & run risk estimate on submit
@app.callback(Output('risk_estimate_variable', 'children'), Input('submit_button', 'n_clicks'),
              state=[State('time_option', 'value'), State('state', 'value'), 
			  State('locations', 'value'), Input('date_picker', 'start_date'), Input('date_picker', 'end_date')])
def run_risk_estimate(n_clicks, time_option, state, locations, start_date, end_date): 
	# if n_clicks:
	import time
	time.sleep(2)
	ODflows = get_fb_data(time_option, state_acronym_map[state], start_date, end_date)
	risk_estimate = get_fb_risk(ODflows, locations, state) 
	return json.dumps(risk_estimate)



# Update Choropleth
import geopandas
print('Reading in geopandas')
full_geo_df = geopandas.read_file(here+"/data/LGA_small_02.geojson")
full_geo_df.id = pd.to_numeric(full_geo_df.id)
full_geo_df.LGA_CODE19 = pd.to_numeric(full_geo_df.LGA_CODE19)
full_geo_df.AREASQKM19 = pd.to_numeric(full_geo_df.AREASQKM19)
full_geo_df.STE_CODE16 = pd.to_numeric(full_geo_df.STE_CODE16)
full_geo_df = full_geo_df.set_index('id')

cbd_lat_longs = {
	1: {"lat": -33.8708, "lon": 151.2073},
	2: {"lat": -37.8136, "lon": 144.9631},
	3: {"lat": -27.4698, "lon": 153.0251},
	4: {"lat": -34.9285, "lon": 138.6007},
	5: {"lat": -31.9505, "lon": 115.8605},
	6: {"lat": -42.8821, "lon": 147.3272},
	7: {"lat": -12.4634, "lon": 130.8456}
}

@app.callback(Output('choropleth', 'figure'), Input('risk_estimate_variable', 'children'), state = [State('state', 'value'), State('locations','value')])
def update_choropleth(risk_estimate, state, locations):
	if risk_estimate:
		# Load in risk estimate
		risk_estimate = json.loads(risk_estimate)
		risk_estimate = {int(k):v for k,v in risk_estimate.items()}

		
		# Loading in state geopandas 
		state_geo_df = full_geo_df[full_geo_df.STE_CODE16 == state]
		state_geo_df = state_geo_df[state_geo_df.LGA_CODE19.apply(
		    lambda x: x in risk_estimate)]
		state_geo_df['Risk Potential'] = [risk_estimate[code]
                                    for code in state_geo_df.index]
		print('Making choropleth with %d rows of LGA\'s' % len(state_geo_df))

		# Create plot
		fig = px.choropleth_mapbox(state_geo_df,
							geojson=state_geo_df.geometry, 
							locations=state_geo_df.index, 
                             color='Risk Potential',
							hover_name='LGA_NAME19',
							color_continuous_scale='reds',
							center=cbd_lat_longs[state],
							mapbox_style="carto-positron",
							zoom=8, opacity=0.8)
		fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

		return fig

	else:
		print('No risk estimate')
		fig = px.choropleth_mapbox([], geojson={}, locations=[1],  
                              center=cbd_lat_longs[state], mapbox_style="carto-positron", 
							  zoom=8)
		fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
		return fig


# High risk location callback
import re
@app.callback(Output('high_risk_areas', 'figure'), Input('risk_estimate_variable', 'children'))
def update_high_risk_areas(risk_estimate):
	if risk_estimate:
		risk_estimate = json.loads(risk_estimate)
		risk_estimate = {int(k):v for k,v in risk_estimate.items()}

		top_risk_tuples = list(sorted(risk_estimate.items(), key=lambda x: x[1]))[-10:]
		y = [lga_name_map.get(n, 'Error') for n, r in top_risk_tuples]
		x = [r for n, r in top_risk_tuples]
		fig = go.Figure(data=[go.Bar(x=x, y=y, orientation='h',
                               marker=dict(color=x, cmin=0, colorscale='reds'))])
		fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

		# content = [lga_name_map.get(c, 'Error') + " %.2f" % r for c,r in sorted(risk_estimate.items(), key = lambda x:x[1], reverse = True) ][:10]
		# md = dcc.Markdown( "\n \n".join(content) ),
		return fig
	else:
		print('Showing empty high risk areas graph')
		return empty_graph


# Download CSV on Button Press
@app.callback( Output("download_div", "data"), Input("download_button", "n_clicks"), 
               state=[State('risk_estimate_variable', 'children'), State('state', 'value')])
def generate_csv(n_clicks, risk_estimate_variable, state):
	if risk_estimate_variable:
		risk_estimate = json.loads(risk_estimate_variable)
		risk_estimate = {int(k): v for k, v in risk_estimate.items()}

		state_geo_df = full_geo_df[full_geo_df.STE_CODE16 == state]
		state_geo_df = state_geo_df[state_geo_df.LGA_CODE19.apply(
		    lambda x: x in risk_estimate)]
		
		state_geo_df['Risk Potential'] = [risk_estimate[code]
                                    for code in state_geo_df.index]

		state_geo_df = state_geo_df[["LGA_CODE19","LGA_NAME19",
                    "STE_NAME16", "AREASQKM19", 'Risk Potential']]

		return send_data_frame(state_geo_df.to_csv, filename="Risk_by_LGA.csv")


server = app.server # the Flask app

# Run
if __name__ == '__main__':
	app.run_server(debug=True)

