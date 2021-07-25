from .server import app, server
from .addInsightsLayouts import *
from .facebookLayout import *
from .googleMobilityLayout import *

app.layout = html.Div(style={'margin':20}, children = [
    html.Div([html.H1("COVID-19 Risk Mapping")], className="row",  style={'textAlign': "center"}),
    html.Div(className="row", style={'textAlign': "justify", 'padding-right': '30px', 'padding-left': '30px'},
		children = dcc.Markdown(d(
		"""
		COVID-19 is highly transmissible and containing outbreaks requires a rapid and effective response. Because infection may be spread by people who are pre-symptomatic or asymptomatic, substantial undetected transmission is likely to occur before clinical cases are diagnosed. When outbreaks occur there is a need to anticipate which populations and locations are at heightened risk of exposure. This app uses aggregated human mobility data for estimating the geographical distribution of transmission risk.
		"""
		))),
    dcc.Tabs([
        dcc.Tab(label='Google Mobility Data', children=googleLayout),
        dcc.Tab(label='Traffic Data (AddInsights)', children=addInsightsLayout),
        dcc.Tab(label='Facebook Mobility Data', children=facebookLayout),
    ]),
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

            #### Acknowledgements
            This app was made by Tobin South with signifcant contributions from Lewis Mitchell, Cameron Zachreson, Peter Dawson, Nicholas Geard, Glenn Burgess, Bradley Donnelly. Thanks Nic Rebuli for the idea to include Google Data. 
            """
    ))),
])

if __name__ == '__main__':
    app.run_server(debug=True)
