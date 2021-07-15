from .server import app

# Import Dash components
import dash
import dash_core_components as dcc
import dash_html_components as html
from textwrap import dedent as d
from numpy import empty # For writing markdown text
import plotly.express as px
from dash.dependencies import Output, Input, State
from datetime import *

from .googleMobilityFunctions import *


googleLayout = html.Div(style={'margin':20}, children = [
    html.Div(className="row", style={'textAlign': "justify", 'padding-right': '30px', 'padding-left': '30px'},
        children = dcc.Markdown(d(
        """
        ### Transmission Risk Between Local Government Areas
        """
        ))),
    # Input selectors
    html.Div(className="row border border-secondary", style={'textAlign': "center"}, children=
            dcc.Markdown(d("""
                        Select an Australian state and a variable from Google's Community Mobility Reports to examine at the LGA level. Please not that this data has an up-to 5 days lag on Google's side. The data uses anonymised and aggregated data from Google Maps. Some LGA's do not have enough users on a given day and will not included a datapoint; this is especially true in regional areas. Also consider that there are two weekend & holiday effects in the data.
                        """)),
    ),
    html.Div(className="row border border-secondary", style={'textAlign': "center", 'padding-right': '30px', 'padding-left': '30px'},
        children=[
            # Variable picker
            html.Div(
                className="six columns",
                children=[
                    dcc.Markdown(d("""
                        #### Select Mobility Variable of Interest
                        """)),
                    dcc.Dropdown(
                        id = 'variable_option_G',
                        options=[
                            {'label':"Retail and recreation", 'value':'retail_and_recreation_percent_change_from_baseline'},
                            {'label':"Supermarket and pharmacy", 'value':'grocery_and_pharmacy_percent_change_from_baseline'},
                            {'label':"Parks", 'value':'parks_percent_change_from_baseline'},
                            {'label':"Public transport", 'value':'transit_stations_percent_change_from_baseline'},
                            {'label':"Workplaces", 'value':'workplaces_percent_change_from_baseline'},
                            {'label':"Residential", 'value':'residential_percent_change_from_baseline'},
                        ],
                        value='workplaces_percent_change_from_baseline',
                        searchable=False,
                    ),
                ]
            ),
            # State picker
            html.Div(
                className="six columns",
                children=[
                    dcc.Markdown(d("""
                        #### Select State
                        """)),
                    dcc.Dropdown(
                        id = 'state_G',
                        options= [ {'label':s, 'value':s} for s in states],
                        value='New South Wales',
                        searchable=False
                    ),
                ]
            ),
        ]
    ),
    html.Hr(),
    html.Div(className="row border border-secondary", style={'textAlign': "center", 'padding-above': '30px', }, id='google_variable_description'),
    html.Hr(),
    # html.Div(className="row border border-secondary", style={'textAlign': "center"}, children=
    #         dcc.Markdown(d("""
    #                     Optionally, 
    #                     """)),
    # ),
    html.Div(className="row border border-secondary", style={'textAlign': "center", 'padding-right': '30px', 'padding-left': '30px', 'max-width':'800px', 'margin':'auto'},  children = [
            html.Div(className="six columns",  children = [    
                dcc.Markdown(d("""
                        #### Display Options
                        """)),
                dcc.Dropdown(id='baseline_or_difference_G',
                            options=[
                                {'label': 'Show difference from March 2020 baseline', 'value': 'baseline'},
                                {'label': 'Show difference from one week ago', 'value': 'difference'},
                                ], value='baseline', className="twelve columns"),
                # dcc.Checklist(id='show_low_flow_G',
                #             options=[{'label': 'Exclude very low risk areas from display', 'value': 1}], value=[], className="twelve columns"),
            ]),
            # Date picker
            html.Div(
                className="six columns", 
                children=[
                    dcc.Markdown(d("""
                        #### Timeline Start Date
                        """)),
                    dcc.DatePickerSingle(
                        id='start_date_G',
                        min_date_allowed=date(2020,2,15),
                        max_date_allowed=date.today(),
                        date = date(2020,2,15),
                    ),
                ]
            ),
    ]),
    # dcc.Markdown(d("""
    #         After selecting the desired inputs, **click the Create Risk Estimate button** to begin calculation. This may take several seconds to process and display depending on your hardware.
    #     """), style={'textAlign': "center", "margin-top": "15px"}),
    # html.Hr(),
    # Submit button
    # dcc.Loading(
    #         id="loading-bar_FB",
    #         type="default",
    #         children=[
    #             html.Div(
    #                 className="row",  style={'textAlign': "center"}, 
    #                 children=[
    #                     html.Button("Create Risk Estimate", id="submit_button_FB", style={
    #                                 'width': '250px', 'height': '60px', 'textAlign': "center", 'horizontalAlign':'center'})
    #                     ]
    #             ),
    #             # Hidden div inside the app that stores the risk values
    #             html.Div(id='risk_estimate_variable_FB', style={'display': 'none'}),
    #             html.Div(id="loading-output_FB")
    #         ]
    # ),
    html.Hr(),
    html.Div(className="row border border-secondary", style={'textAlign': "center", 'padding-right': '30px', 'padding-left': '30px', 'max-width':'800px', 'margin':'auto'}, id='latest_date_google', 
    children=dcc.Markdown(d("""##### The latest available Google Mobility Data is from %s""" % latest_date.strftime('%Y-%m-%d')))
    ),
    html.Hr(),
    # Plots 
    dcc.Loading(
            id="loading-bar_G-figures",
            type="default",
            # color='#e0a12b',
            children=[
                html.Div(
                    className="row",
                    children=[            
                        html.Div(
                            className="seven columns",
                            children=[
                                dcc.Graph(id="choropleth_G", figure=empty_graph)
                            ]
                        ),
                        html.Div(
                            className="five columns",
                            children=[
                                dcc.Graph(id='change_over_time_G', figure=instruction_graph)
                            ]

                        ),
                    ]
                ),
            ]
    ),
    html.Hr(),
    html.Div(
        className="row",  style={'textAlign': "center"}, 
        children=html.A(html.Button('Download Data'), href='https://www.google.com/covid19/mobility/')
    ),

])

############################################################################################################################
# These callbacks are what will make everything interactive
############################################################################################################################

@app.callback(Output('google_variable_description','children'), Input('variable_option_G', 'value'))
def updated_description(variable_option_G):
    return "Mobility variable description: " + explainer_variable_mapping[variable_option_G]

@app.callback(Output('choropleth_G', 'figure'), Input('baseline_or_difference_G', 'value'), Input('state_G', 'value'), Input('variable_option_G', 'value'))
def update_choropleth_FB(baseline_or_difference_G, state_G, variable_option_G,):

    googleState = google[google['state'] == state_G]
    current_data = googleState[googleState.date == latest_date][['LGA',variable_option_G]].dropna().set_index('LGA')[variable_option_G]
    if baseline_or_difference_G == 'difference':
        one_week_data = googleState[googleState.date == latest_date - pd.Timedelta(days=7)][['LGA',variable_option_G]].dropna().set_index('LGA')[variable_option_G]
        difference_data = current_data - one_week_data
        data = difference_data
        color_name = 'Change from last week'
        title =  "Current difference in %s mobility compared to last week" % nice_variable_names[variable_option_G]
    else:
        data = current_data
        color_name = 'Change from baseline'
        title =  "Current difference in %s mobility compared to baseline" % nice_variable_names[variable_option_G]
   
    state_geo_df = full_geo_df[full_geo_df.STE_NAME16 == state_G]
    state_geo_df = state_geo_df[state_geo_df.LGA_NAME19.apply(lambda x: x in data.index)]
    state_geo_df[color_name] = state_geo_df.LGA_NAME19.map(data.to_dict())

    fig = px.choropleth_mapbox(state_geo_df,
                                geojson=state_geo_df.geometry, 
                                locations=state_geo_df.index, 
                                hover_name='LGA_NAME19',
                                color=color_name,
                                color_continuous_scale='RdBu_r',
                                center=cbd_lat_longs[state_G], 
                                mapbox_style="carto-positron",
                                zoom=9, opacity=0.8,
                                title=title)
    fig.update_layout(margin={"r":0,"t":40,"l":0,"b":0})
    return fig


@app.callback(Output('change_over_time_G', 'figure'), Input('choropleth_G', 'clickData'), Input('state_G','value'), Input('start_date_G','date'), Input('variable_option_G','value'))
def update_time_plot(clickData, state_G, start_date_G, variable_option_G):
    if clickData is not None:
        this_LGA = clickData['points'][0]['hovertext']
        googleState = google[google['state'] == state_G]
        if start_date_G != date(2020,2,15):
            googleState = googleState[googleState.date > start_date_G]
        data = googleState[googleState.LGA == this_LGA][['date', variable_option_G]].dropna().sort_values('date')
        fig = px.line(data, x = 'date', y=variable_option_G, title="Change in %s over time in %s" % (nice_variable_names[variable_option_G], this_LGA))
        fig.add_hline(y=0, line_dash="dash", name="Baseline")
        fig.update_layout(margin={"r":0,"t":40,"l":0,"b":0})
        fig.update_layout(xaxis_title="Date",yaxis_title=nice_variable_names[variable_option_G])
        return fig
    else:
        return instruction_graph
