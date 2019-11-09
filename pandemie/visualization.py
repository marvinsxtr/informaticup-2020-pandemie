import json
import os

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = html.Div(
    html.Div([
        html.H3('Pandemie!'),
        html.Div(id='game-state'),
        dcc.Interval(
            id='interval-component',
            interval=100,  # in millis
            n_intervals=0
        )
    ])
)


@app.callback(Output('game-state', 'children'),
              [Input('interval-component', 'n_intervals')])
def update_game_state(n):
    f = open(os.getcwd() + "/tester/tmp/current_json.dat", "r")
    json_data = json.loads(f.read())

    return [html.Span('Round: {0}'.format(json_data["round"]), style={'padding': '5px', 'fontSize': '16px'})]


if __name__ == "__main__":
    app.run_server(debug=False)
