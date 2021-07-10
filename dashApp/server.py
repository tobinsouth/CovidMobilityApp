import dash
from .params import requests_pathname_prefix

app = dash.Dash(__name__, external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'],
                requests_pathname_prefix=requests_pathname_prefix) 

app.title = "COVID-19 Spatial Risk Map"

# styles: for right side hover/click component
styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}

server = app.server