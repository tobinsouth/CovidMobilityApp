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

######################################################################################################################################################################
# This is the setup of the actual dash html interface
######################################################################################################################################################################

# import the css template, and pass the css template into dash
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "Network"

# styles: for right side hover/click component
styles = {
	'pre': {
		'border': 'thin lightgrey solid',
		'overflowX': 'scroll'
	}
}

app.layout = html.Div([
	# Title & Explainer
	html.Div([html.H1("COVID Risk Mapping")], className="row",  style={'textAlign': "center"}),
	# html.Div(className="row", 
	#     children = dcc.Markdown(d("""
	#                     About this
	#                     """)),
	#         ),
	html.Div(className="row"),
	# Input selectors
	html.Div(
		className="row border border-secondary", style={'textAlign': "center"}, 
		children=[
			# Date picker
			html.Div(
				className="three columns", 
				children=[
					dcc.Markdown(d("""
						#### Select date
						""")),
					dcc.DatePickerSingle(
						id='date_picker',
						min_date_allowed=date(2020, 5, 1),
						max_date_allowed=date.today(),
						date = date(2021, 1, 1),
					),
					# html.Div(id='show-date_picker')
				]
			),
			# Time picker
			html.Div(
				className="two columns",
				children=[
					dcc.Markdown(d("""
						#### Select times
						""")),
					dcc.Dropdown(
						id = 'time_option',
						options=[
							{'label': 'Morning', 'value': 0},
							{'label': 'Afternoon', 'value': 800},
							{'label': 'Night', 'value': 1600}
						],
						value=0,
						searchable=False
						# labelStyle={'display': 'inline-block'}
					),
					# html.Div(id = "show-selected_times")
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
					# dcc.Markdown(d("""
					# 	Mobility data is only considered within-state. 
					# 	""")),
					html.Div(id = "show-selected_times")
				]
			),
			# Location picker
			html.Div(
				className="four columns",
				children=[
					dcc.Markdown(d("""
						#### High Risk Locations
						""")),
					dcc.Dropdown(
						id='locations',
						options= [ {'label':v, 'value':k} for k,v in lga_name_map.items() if k // 10000 == 1],
						value= [],
						multi=True
					),
					dcc.Checklist(id='select-all-from-dropdown',
						options=[{'label': 'Select All', 'value': 1}], value=[]),
					html.Div(id='show-locations'),
				]
			)
		]
	),
	dcc.Markdown(d("""
		Mobility data from Facebook is collected to quantify the movement of individuals between local government areas (LGA). A risk estimate is generated based on the locations included in High Risk Locations. Risk spreads from these locations into other LGAs where people often travel to after visiting the high risk locations. When no locations are selected, a general risk estimate will be shown.		
		""")),
	html.Hr(),
	# Submit button
	html.Div(
		className="row",  style={'textAlign': "center"}, 
		children=[
			html.Button("Create Risk Estimate", id="submit_button")
			]
	),
	html.Hr(),
	# Plots 
	html.Div(
		className="row",
		children=[            
			html.Div(
				className="eight columns",
				children=[
					dcc.Markdown(d("""
						### Risk Map:
						""")),
					dcc.Graph(id="choropleth", 
						figure= px.choropleth_mapbox([], geojson={}, 
							locations=[1],  
							center=cbd_lat_longs[1], 
							mapbox_style= "carto-positron", zoom=8)
						)
				]
			),
			html.Div(
				className="four columns",
				children=[
					dcc.Markdown(d("""
						### Highest Risk Areas:
						""")),
					dcc.Graph(id = 'high_risk_areas')
				]

			),
		]
	),
	html.Hr(),
	html.Div(
		className="row",  style={'textAlign': "center"}, 
		children=[
			html.Button("Download Flow Matrix as CSV", id="download_button")
			]
	),

	# Hidden div inside the app that stores the risk values
	html.Div(id='risk_estimate_variable', style={'display': 'none'}),

	# Element to allow for file download
	Download(id="download_div"),
])

######################################################################################################################################################################
# These callbacks are what will make everything interactive
######################################################################################################################################################################

# Show selected locations
@app.callback(Output('show-locations', 'children'), Input('locations', 'value'), State('select-all-from-dropdown', 'value'))
def display_locations(values, all_option):
	if len(values)==0:
		return None #"No locations selected, will show generalized risk estimate."
	if all_option != []:
		if all_option[0] == 1:
			return "All possible locations selected, which is pretty much the same thing as selecting no locations."
	return None # "Selected %d locations. Risk map will be estimated starting from these locations." % len(values)
	# return ", ".join(values)


# Select all possible starting locations.
@app.callback( Output('locations', 'value'),
	[Input('select-all-from-dropdown', 'value')],
	[State('locations', 'options'),
	 State('locations', 'value')])
def select_all_locations(selected, options, values):
	if selected != []:
		if selected[0] == 1:
			return [i['value'] for i in options]
	return values

# Update location list according to state
@app.callback(Output('locations', 'options'),
              [Input('state', 'value')])
def update_possible_state_locations(state):
	return [{'label': v, 'value': k} for k, v in lga_name_map.items() if k // 10000 == state]


# Get new data & run risk estimate on submit
@app.callback(Output('risk_estimate_variable', 'children'), Input('submit_button', 'n_clicks'),
              state=[State('date_picker', 'date'), State('time_option', 'value'), State('state', 'value'), 
			  State('locations', 'value')])
def run_risk_estimate(n_clicks, date, time_option, state, locations): 
	ODflows = get_fb_data(date, time_option, state_acronym_map[state])
	risk_estimate = get_fb_risk(ODflows, locations, state) 
	return json.dumps(risk_estimate)

# Update Choropleth
import geopandas

full_geo_df = geopandas.read_file("data/LGA_small_01.geojson")
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
		return None
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
		return None


# Download CSV on Button Press
@app.callback( Output("download_div", "data"), Input("download_button", "n_clicks"), 
               state=[State('risk_estimate_variable', 'children'), State('state', 'value')])
def generate_csv(n_clicks, risk_estimate_variable, state):
	if risk_estimate_variable:
		risk_estimate = json.loads(risk_estimate)
		risk_estimate = {int(k): v for k, v in risk_estimate.items()}

		state_geo_df = full_geo_df[full_geo_df.STE_CODE16 == state]
		state_geo_df = state_geo_df[state_geo_df.LGA_CODE19.apply(
		    lambda x: x in risk_estimate)]
		
		state_geo_df['Risk Potential'] = [risk_estimate[code]
                                    for code in state_geo_df.index]

		state_geo_df = state_geo_df[["LGA_CODE19" "LGA_NAME19",
                    "STE_NAME16", "AREASQKM19", 'Risk Potential']]

		return send_data_frame(state_geo_df.to_csv, filename="Risk_by_LGA.csv")

# Run
if __name__ == '__main__':
	app.run_server(debug=True)

