from .server import app

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
from .facebookFunctions import *


facebookLayout = html.Div(style={'margin':20}, children = [
	html.Div(className="row", style={'textAlign': "justify", 'padding-right': '30px', 'padding-left': '30px'},
		children = dcc.Markdown(d(
		"""
		### Transmission Risk Between Local Goverment Areas
		
		This section's aggregate data is provided by [Facebook's Data for Good](https://dataforgood.fb.com/) initiative. To learn more about the methods used here, their reliability and their applicability, read [Risk mapping for COVID-19 outbreaks in Australia using mobility data](https://royalsocietypublishing.org/doi/full/10.1098/rsif.2020.0657).

		To use the app select a range of dates and times to aggregate mobility data over for a state. Outbreaks may be started from any set of local government areas. A generalised risk profile will be generated when no locations are selected.

		**Note:** The data from Facebook has changed format and is not long being updated. If there is an ongoing interest in using this product please contact [the data maintainer](mailto:cameron.zachreson@unimelb.edu.au) to request updated data.
		"""
		))),
	html.Hr(),
	# Input selectors
	html.Div(className="row border border-secondary", style={'textAlign': "center"}, children=
			dcc.Markdown(d("""
						Select a set of dates and times of day to collect mobility data over. This data is used to create a network of movement between local government areas to help examine the risk of spread.
						""")),
	),
	html.Div(className="row border border-secondary", style={'textAlign': "center", 'padding-right': '30px', 'padding-left': '30px'},
		children=[
			# Date picker
			html.Div(
				className="four columns", 
				children=[
					dcc.Markdown(d("""
						#### Select Dates
						""")),
					dcc.DatePickerRange(
                        id='date_picker_FB',
                        min_date_allowed=date(2020, 5, 1),
                        max_date_allowed=date.today()-timedelta(1),
                        start_date = pd.to_datetime('2021-02-01'),
                        end_date= pd.to_datetime('2021-02-03'),
						display_format='DD/MM/YY',
						minimum_nights=0,
                    ),
					# dcc.DatePickerSingle(
					# 	id='date_picker_FB',
					# 	min_date_allowed=date(2020, 5, 1),
					# 	max_date_allowed=date.today(),
					# 	date = date(2021, 1, 1),
					# ),
				]
			),
			# Time picker
			html.Div(
				className="four columns",
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
						value='*',
						searchable=False,
					),
				]
			),
			# State picker
			html.Div(
				className="four columns",
				children=[
					dcc.Markdown(d("""
						#### Select State
						""")),
					dcc.Dropdown(
						id = 'state',
						options= [ {'label':v, 'value':k} for k,v in state_fullname_map.items()],
						value=1,
						searchable=False
					),
				]
			),
		]
	),
	html.Hr(),
	html.Div(className="row border border-secondary", style={'textAlign': "center"}, children=
			dcc.Markdown(d("""
						Optionally, select location to examine how people travel out of an area or set of areas. If no locations are selected, a general mobility risk map will be shown.
						""")),
	),
	html.Div(className="row border border-secondary", style={'textAlign': "center", 'padding-right': '30px', 'padding-left': '30px'},  children = [
		# Location picker
			html.Div(
				className="eight columns",
				children=[
					dcc.Markdown(d("""
						#### Outbreak Centres
						""")),
					dcc.Dropdown(
						id='locations_FB',
						options= [ {'label':v, 'value':k} for k,v in lga_name_map.items() if k // 10000 == 1],
						value= [],
						multi=True,
						placeholder="Optional -  Select Outbreak Startpoints",
					),
				]
			),
			html.Div(className="four columns",  children = [	
				dcc.Markdown(d("""
						#### Display Options
						""")),
				dcc.Checklist(id='show_outbreak_centres_FB',
							options=[{'label': 'Exclude outbreak startpoints from display', 'value': 1}], value=[], className="twelve columns"),
				dcc.Checklist(id='show_low_flow_FB',
							options=[{'label': 'Exclude very low risk areas from display', 'value': 1}], value=[], className="twelve columns"),
			]),
	]),
	dcc.Markdown(d("""
			After selecting the desired inputs, **click the Create Risk Estimate button** to begin calculation. This may take several seconds to process and display depending on your hardware.
		"""), style={'textAlign': "center", "margin-top": "15px"}),
	html.Hr(),
	# Submit button
	dcc.Loading(
            id="loading-bar_FB",
            type="default",
			children=[
				html.Div(
					className="row",  style={'textAlign': "center"}, 
					children=[
						html.Button("Create Risk Estimate", id="submit_button_FB", style={
						            'width': '250px', 'height': '60px', 'textAlign': "center", 'horizontalAlign':'center'})
						]
				),
				# Hidden div inside the app that stores the risk values
				html.Div(id='risk_estimate_variable_FB', style={'display': 'none'}),
				html.Div(id="loading-output_FB")
			]
	),
	html.Hr(),
	# Plots 
	dcc.Loading(
            id="loading-bar_FB-figures",
            type="default",
			color='#e0a12b',
			children=[
				html.Div(
					className="row",
					children=[            
						html.Div(
							className="eight columns",
							children=[
								dcc.Markdown(d("""
									### Relative Spatial Risk Map:
									""")),
								dcc.Graph(id="choropleth_FB", figure=empty_graph)
							]
						),
						html.Div(
							className="four columns",
							children=[
								dcc.Markdown(d("""
									### Highest Risk Areas:
									""")),
								dcc.Graph(id='high_risk_areas_FB', figure=empty_graph)
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
			html.Button("Download Risk Potential as CSV", id="download_button_FB")
			]
	),
	# Element to allow for file download
	Download(id="download_div_FB"),
])

############################################################################################################################
# These callbacks are what will make everything interactive
############################################################################################################################

# Update location list according to state
@app.callback(Output('locations_FB', 'options'),
              [Input('state', 'value')])
def update_possible_state_locations_FB(state):
	return [{'label': v, 'value': k} for k, v in lga_name_map.items() if k // 10000 == state]


# Get new data & run risk estimate on submit
@app.callback(Output('risk_estimate_variable_FB', 'children'), Input('submit_button_FB', 'n_clicks'), Input('time_option', 'value'), Input('state', 'value'), Input('locations_FB', 'value'), Input('date_picker_FB', 'start_date'), Input('date_picker_FB', 'end_date'))
def run_risk_estimate(n_clicks, time_option, state, locations_FB, start_date, end_date): 
	ctx = dash.callback_context
	if not ctx.triggered:
		ODflows = get_fb_data(time_option, state_acronym_map[state], start_date, end_date)
		risk_estimate = get_fb_risk(ODflows, locations_FB, state) 
		return json.dumps(risk_estimate)
	else:
		change_prop_id = ctx.triggered[0]['prop_id'].split('.')[0]
		if change_prop_id == 'submit_button_FB':
			ODflows = get_fb_data(time_option, state_acronym_map[state], start_date, end_date)
			risk_estimate = get_fb_risk(ODflows, locations_FB, state)
			return json.dumps(risk_estimate)
		else:
			return -1


@app.callback(Output('choropleth_FB', 'figure'), Input('risk_estimate_variable_FB', 'children'), Input('show_outbreak_centres_FB', 'value'), Input('show_low_flow_FB', 'value'), state = [State('state', 'value'), State('locations_FB','value')])
def update_choropleth_FB(risk_estimate, show_outbreak_centres_FB, show_low_flow_FB, state, locations_FB):
	if risk_estimate and (risk_estimate != -1):
		# Load in risk estimate
		risk_estimate = json.loads(risk_estimate)
		risk_estimate = {int(k):v for k,v in risk_estimate.items()}# Fix keys

		# Removing outbreak centres if desired
		if len(show_outbreak_centres_FB)!=0 and len(locations_FB) > 0:
			risk_estimate = {k:v for k,v in risk_estimate.items() if int(k) not in locations_FB}

		# Removing 0 flow areas
		if len(show_low_flow_FB) != 0:
			risk_estimate = {k:v for k,v in risk_estimate.items() if v != 0}

		# Log transform for colourscale
		risk_estimate_log = {k:np.log10(v+10**(-10)) for k,v in risk_estimate.items()}

		# Loading in state geopandas 
		state_geo_df = full_geo_df[full_geo_df.STE_CODE16 == state]
		state_geo_df = state_geo_df[state_geo_df.LGA_CODE19.apply(
		    lambda x: x in risk_estimate)]
		state_geo_df['Log10 Risk Potential'] = [risk_estimate_log[code] for code in state_geo_df.index]
		state_geo_df['Relative Risk Potential'] = [risk_estimate[code] for code in state_geo_df.index]

		# Create plot
		fig = px.choropleth_mapbox(state_geo_df,
							geojson=state_geo_df.geometry, 
							locations=state_geo_df.index, 
							hover_name='LGA_NAME19',
                            color='Log10 Risk Potential',
							color_continuous_scale='reds',
							center=cbd_lat_longs[state],
							mapbox_style="carto-positron",
							zoom=8, opacity=0.8)

		customdata  = np.stack([state_geo_df[col] for col in ["Relative Risk Potential", "LGA_NAME19", "AREASQKM19", "Population", "Median Age"]], axis=-1)
		fig.update_traces(customdata = customdata, hovertemplate='<b>%{customdata[1]}</b> <br>'+
										'Relative Risk Potential: %{customdata[0]} <br>'+
										'Population: %{customdata[3]} <br>'+
										'Median Age: %{customdata[4]} <br>'+
										'Area (km^2): %{customdata[2]} <br>')

		# This fixes the log colourscale to show the original values
		min_vals = min(risk_estimate_log.values())
		max_vals = max(risk_estimate_log.values())
		tickvals = [round(n, 4) for n in np.logspace(min_vals, max_vals, num = 6)]
		ticktext = [str(v) for v in tickvals]
		tickvals = [np.log10(v+10**(-10)) for v in tickvals]

		coloraxis = fig['layout']['coloraxis']
		coloraxis['colorbar']['tickvals'] = tickvals
		coloraxis['colorbar']['ticktext'] = ticktext
		coloraxis['colorbar']['title']['text'] = "Relative Risk\nPotential"

		fig.update_layout(coloraxis=coloraxis)

		fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

		return fig

	else:
		return empty_graph


# High risk location callback
@app.callback(Output('high_risk_areas_FB', 'figure'), Input('risk_estimate_variable_FB', 'children'), Input('show_outbreak_centres_FB', 'value'), Input('show_low_flow_FB', 'value'),state = [State('state', 'value'), State('locations_FB','value')]) 
def update_high_risk_areas_FB(risk_estimate, show_outbreak_centres_FB, show_low_flow_FB, state, locations_FB):
	if risk_estimate and (risk_estimate != -1):
		risk_estimate = json.loads(risk_estimate)
		risk_estimate = {int(k):v for k,v in risk_estimate.items()}# Fix keys

		# Removing outbreak centres if desired
		if len(show_outbreak_centres_FB)!=0 and len(locations_FB) > 0:
			risk_estimate = {k:v for k,v in risk_estimate.items() if k not in locations_FB}

		# Removing 0 flow areas
		if len(show_low_flow_FB) != 0:
			risk_estimate = {k:v for k,v in risk_estimate.items() if v != 0}
		
		top_risk_tuples = list(sorted(risk_estimate.items(), key=lambda x: x[1]))[-10:]
		y = [lga_name_map.get(n, 'Error') for n, r in top_risk_tuples]
		x = np.array([r for n, r in top_risk_tuples])

		top_risk_tuples_log = [np.log10(v+10**(-10)) for k,v in top_risk_tuples]# Log transform for colourscale
		
		fig = go.Figure(data=[go.Bar(x=x, y=y, orientation='h', hoverinfo='skip',
                               marker=dict(color=top_risk_tuples_log, cmin=0, colorscale='reds'))])

		fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

		return fig
	else:
		return empty_graph


# Download CSV on Button Press
@app.callback( Output("download_div_FB", "data"), Input("download_button_FB", "n_clicks"), 
               state=[State('risk_estimate_variable_FB', 'children'), State('state', 'value')])
def generate_csv(n_clicks, risk_estimate_variable_FB, state):
	if risk_estimate_variable_FB:
		risk_estimate = json.loads(risk_estimate_variable_FB)
		risk_estimate = {int(k): v for k, v in risk_estimate.items()}

		state_geo_df = full_geo_df[full_geo_df.STE_CODE16 == state]
		state_geo_df = state_geo_df[state_geo_df.LGA_CODE19.apply(
		    lambda x: x in risk_estimate)]
		
		state_geo_df['Risk Potential'] = [risk_estimate[code]
                                    for code in state_geo_df.index]

		state_geo_df = state_geo_df[["LGA_CODE19","LGA_NAME19",
                    "STE_NAME16", "AREASQKM19", 'Risk Potential']]

		return send_data_frame(state_geo_df.to_csv, filename="Risk_by_LGA.csv")