from dashApp.allLayouts import app
from dashApp.params import debug

if __name__ == '__main__':
    app.run_server(debug=debug)

server = app.server

# https://community.plotly.com/t/splitting-callback-definitions-in-multiple-files/10583/2