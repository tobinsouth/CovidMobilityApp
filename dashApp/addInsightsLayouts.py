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

# For downloading csv
from dash_extensions import Download
from dash_extensions.snippets import send_data_frame

# Import AddInsights functions
from .addInsightFunctions import *

from datetime import *
import geopandas 
import pandas as pd

# Add Insights connection functions

ai_connection = connectionSetup() # Connection client
geosDF = geopandas.read_file(here + '/data/SA2GeoJson.gjson')
groupIds =  list(geosDF.id)


##################################################################################
# This is the setup of the actual dash html interface
##################################################################################


addInsightsLayout = html.Div(style={'margin':20}, children = [
    html.Div(className="row", style={'textAlign': "justify", 'padding-right': '30px', 'padding-left': '30px'},
        children = dcc.Markdown(d(
        """
        ### Transmission Risk Between SA2 areas in South Australia

        This section's aggregate data is provided by Addinsight from the Department for Infrastructure and Transport (DIT). Addinsight is an Intelligent Transport System (ITS) that collects car data from road network hardware.

        To use the app select a range of dates and times to aggregate mobility data over for a state. Outbreaks may be started from any set of SA2 regions. A generalised risk profile will be generated when no locations are selected.
        """
        ))),
    html.Hr(),
	# Input selectors
	html.Div(className="row border border-secondary", style={'textAlign': "center"}, children=
			dcc.Markdown(d("""
						Select a set of dates and times of day to collect mobility data over. This data is used to create a network of movement between local government areas to help examine the risk of spread.
						""")),
	),
    html.Div(
        className="row border border-secondary", style={'textAlign': "center", 'padding-right': '30px', 'padding-left': '30px'},
        children=[
            # Date picker
            html.Div(
                className="six columns", 
                children=[
                    dcc.Markdown(d("""
                        #### Select dates
                        Select your period of time inclusive of start and end date. 
                        Choose the same date if you want a single day.
                        """)),
                    dcc.DatePickerRange(
                        id='date_picker_AI',
                        min_date_allowed=date(2020, 1, 1),
                        max_date_allowed=date.today(),
                        start_date = date.today()-timedelta(8),
                        end_date= date.today()-timedelta(1)
                    ),
                    html.Div(id='show-date_picker_AI')
                ]
            ),
            # Time picker
            html.Div(
                className="six columns", style={'textAlign': "center", 'padding-right': '30px', 'padding-left': '30px'},
                children=[
                    dcc.Markdown(d("""
                        #### Select times of day
                        Only movement data that occurred **during these times** on **each selected date** will be used.
                        """)),
                    html.Div(className = 'row', children = [  
                        html.Div(className = 'six columns', children = [
                                html.Div(className='row',children = "Start Time"),
                                dcc.Input(type='text', id = 'start_time_of_day', placeholder ='Start: 1:00')
                            ]
                        ),
                        html.Div(className = 'six columns', children = [
                                html.Div(className='row',children = "End Time"),
                                dcc.Input(type='text', id = 'end_time_of_day', placeholder = 'End: 23:30')
                            ]
                        ),
                    ]),
                    html.Div(id = "show-selected_times")
                ]
            ),
    ]),
    html.Hr(),
    html.Div(className="row border border-secondary", style={'textAlign': "center"}, children=
			dcc.Markdown(d("""
						Optionally, select locations to examine how people travel out of an area or set of areas. If no locations are selected, a general mobility risk map will be shown.
						""")),
	),
    html.Div(
        className="row border border-secondary", style={'textAlign': "center", 'padding-right': '30px', 'padding-left': '30px'},
        children=[
        # Location picker
            html.Div(
                className="eight columns", style={'textAlign': "center", 'padding-right': '30px', 'padding-left': '30px'},
                children=[
                dcc.Markdown(d("""
                    #### Outbreak Centres
                    """)),
                dcc.Dropdown(
                    id='locations_AI',
                    options= [{'label': value, 'value': key} for key, value in all_sa2_names.items()],
                    value= [],
                    multi=True,
                    placeholder="Optional -  Select Outbreak Startpoints",
                ),
            ]),
            html.Div(className="four columns",  children = [
                dcc.Markdown(d("""
                    #### Display Options
                    """)),
                dcc.Checklist(id='show_outbreak_centres_AI',
                            options=[{'label': 'Exclude outbreak startpoints from display', 'value': 1}], value=[], className="twelve columns"),
                dcc.Checklist(id='show_low_flow_AI',
                            options=[{'label': 'Exclude very low risk areas from display', 'value': 1}], value=[], className="twelve columns"),
                ]),
            ]
    ),
    html.Hr(),
    # Submit button
    html.Div(className="row"),
	dcc.Markdown(d("""
			After selecting the desired inputs, **click the Create Risk Estimate button** to begin calculation. This may take several seconds to process and display depending on your hardware.
		"""), style={'textAlign': "center", "margin-top": "15px"}),
    html.Hr(),
    # Submit button
    dcc.Loading(
            id="loading-bar_AI",
            type="default",
            children=[
                html.Div(
                    className="row",  style={'textAlign': "center"}, 
                    children=[
                        html.Button("Create Risk Estimate", id="submit_button_AI", style={
                                    'width': '250px', 'height': '60px', 'textAlign': "center", 'horizontalAlign':'center'})
                        ]
                ),
                # Hidden div inside the app that stores the risk values
                html.Div(id='risk_estimate_variable_AI', style={'display': 'none'}),
                html.Div(id="loading-output_AI")
            ]
    ),
    html.Hr(),
    # Plots 
    dcc.Loading(
            id="loading-bar_AI-figures",
            type="default",
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
                                dcc.Graph(id="choropleth_AI", figure=empty_graph)
                            ]
                        ),
                        html.Div(
                            className="four columns",
                            children=[
                                dcc.Markdown(d("""
                                    ### Highest Risk Areas:
                                    """)),
                                dcc.Graph(id='high_risk_areas_AI', figure=empty_graph)
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
            html.Button("Download Flow Matrix as CSV", id="download_button_AI")
            ]
    ),

    # Element to allow for file download
    Download(id="download_div_AI"),
])



######################################################################################################################################################################
# These callbacks are what will make everything interactive
######################################################################################################################################################################


# Dates callback
@app.callback(Output('show-date_picker_AI', 'children'),
            [Input('date_picker_AI', 'start_date'),
            Input('date_picker_AI', 'end_date')])
def display_dates(start_date, end_date):
    if (start_date is None) or (end_date is None):
        return "Select dates."
    start_date_string = pd.to_datetime(start_date).strftime("%Y-%m-%d")
    end_date_string = pd.to_datetime(end_date).strftime("%Y-%m-%d")
    if start_date_string == end_date_string:
        return 'Data will be collected for date %s' % start_date_string
    return 'Data will be collected for the included hours from %s to %s' % (start_date_string, end_date_string)


# Time picker callback
import re
@app.callback(Output('show-selected_times', 'children'),
            [Input('start_time_of_day', 'value'), Input('end_time_of_day', 'value')])
def display_times(start_time_of_day, end_time_of_day):
    if (start_time_of_day is None) or (end_time_of_day is None):
        return None
    time_check = re.compile("(24:00|2[0-3]:[0-5][0-9]|[0-1][0-9]:[0-5][0-9]|[0-9]:[0-5][0-9])")
    if not bool(time_check.match(start_time_of_day)):
        return "Please enter a valid start time as HH:MM."
    if not bool(time_check.match(end_time_of_day)):
        return "Please enter a valid end time as HH:MM using 24hr time."
    return "Using data from "+start_time_of_day+" to "+end_time_of_day+" for each date."


# Get new data & run risk estimate on submit
@app.callback(Output('risk_estimate_variable_AI', 'children'), Input('submit_button_AI', 'n_clicks'),Input('date_picker_AI', 'start_date'), Input('date_picker_AI', 'end_date'), Input('start_time_of_day', 'value'), Input('end_time_of_day', 'value'), Input('locations_AI', 'value'))
def run_risk_estimate(n_clicks,start_date, end_date, start_time_of_day, end_time_of_day, locations_AI): 
    ctx = dash.callback_context
    if not ctx.triggered:
        ODflows = getODbySA2(start_date, end_date, start_time_of_day, end_time_of_day, ai_connection, groupIds)
        risk_estimate = get_risk(ODflows, locations_AI) 
        return json.dumps(risk_estimate)
    else:
        change_prop_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if change_prop_id == 'submit_button_AI':
            ODflows = getODbySA2(start_date, end_date, start_time_of_day, end_time_of_day, ai_connection, groupIds)
            risk_estimate = get_risk(ODflows, locations_AI)
            return json.dumps(risk_estimate)
        else:
            return -1

# Update Choropleth
@app.callback(Output('choropleth_AI', 'figure'), Input('risk_estimate_variable_AI', 'children'), Input('show_outbreak_centres_AI', 'value'), Input('show_low_flow_AI', 'value'), Input('locations_AI', 'value'))
def update_choropleth_AI(risk_estimate, show_outbreak_centres_AI, show_low_flow_AI, locations_AI):
    if risk_estimate and (risk_estimate != -1):
        risk_estimate = json.loads(risk_estimate)

        # Log and normalise
        # risk_estimate = {int(k):np.log1p(v)/min(np.log1p(list(risk_estimate.values()))+1) for k,v in risk_estimate.items()}
        risk_estimate = {int(k):v for k,v in risk_estimate.items()}

        # Removing outbreak centres if desired
        if len(show_outbreak_centres_AI)!=0:
            risk_estimate = {k:v for k,v in risk_estimate.items() if k not in locations_AI}

        # Removing 0 flow areas
        if len(show_low_flow_AI) != 0:
            risk_estimate = {k:v for k,v in risk_estimate.items() if v != 0}

        # Log transform for colourscale
        risk_estimate_log = {k:np.log10(v+10**(-10)) for k,v in risk_estimate.items()}
        
        geosDF['risk_estimate'] = geosDF.id.map(risk_estimate)
        geosDF['risk_estimate_log'] = geosDF.id.map(risk_estimate_log)
        temp_geosDF = geosDF.set_index('id')
        fig = px.choropleth_mapbox(temp_geosDF, geojson=temp_geosDF.geometry, 
                                    locations=temp_geosDF.index,
                                    color='risk_estimate_log',
                                    hover_name='normalname',
                                    color_continuous_scale="reds",
                                    center={"lat": -34.908458, "lon": 138.629006},
                                mapbox_style="carto-positron",
                                    zoom=11, opacity=0.8)
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

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

        return fig
    else:
        return empty_graph


# High risk location callback
import re
@app.callback(Output('high_risk_areas_AI', 'figure'), Input('risk_estimate_variable_AI', 'children'), Input('show_outbreak_centres_AI', 'value'), Input('locations_AI', 'value'))
def update_high_risk_areas_AI(risk_estimate, show_outbreak_centres_AI, locations_AI):
    # if risk_estimate:
    #     risk_estimate = json.loads(risk_estimate)
    #     geosDF['risk_estimate'] = geosDF.id.map(risk_estimate)
    #     geosDF = geosDF[['normalname','risk_estimate']].sort_values('risk_estimate', ascending = False)
    #     content = [name + " ("+str(single_outflow)+")"  for _, name, single_outflow in geosDF.iloc[:10].itertuples()]
    #     # print(geos.head())
    #     md = dcc.Markdown( "\n \n".join(content) ),
    #     return md

    if risk_estimate and (risk_estimate != -1):
        risk_estimate = json.loads(risk_estimate)
        

        # Log and normalise
        # risk_estimate = {int(k):np.log1p(v)/min(np.log1p(list(risk_estimate.values()))+1) for k,v in risk_estimate.items()}
        risk_estimate = {int(k):v for k,v in risk_estimate.items()}

        # Removing outbreak centres if desired
        if len(show_outbreak_centres_AI)!=0 and len(locations_AI) > 0:
            print('Removing outbreaks', locations_AI)
            risk_estimate = {k:v for k,v in risk_estimate.items() if k not in locations_AI}
        
        top_risk_tuples = list(sorted(risk_estimate.items(), key=lambda x: x[1]))[-10:]
        y = [all_sa2_names.get(n, 'Error') for n, r in top_risk_tuples]
        x = [r for n, r in top_risk_tuples]
        fig = go.Figure(data=[go.Bar(x=x, y=y, orientation='h',
                            marker=dict(color=x, cmin=0, colorscale='reds'))])
        fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
        return fig
    else:
        return empty_graph

# Download CSV on Button Press
@app.callback( Output("download_div_AI", "data"), [Input("download_button_AI", "n_clicks")], 
    state=[State('risk_estimate_variable_AI', 'children')])
def generate_csv(n_clicks, jsonified_dataframe):
    if jsonified_dataframe:
        print(n_clicks)
        flow_data_long = pd.read_json(jsonified_dataframe, orient='split')
        print(flow_data_long.head())
        return send_data_frame(flow_data_long.to_csv, filename="flow_data_long.csv")


