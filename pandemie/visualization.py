import json
import os

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = 'Pandemie!'
app.layout = html.Div(
    html.Div([
        html.H3('Pandemie!'),
        html.Div(id='game-state'),
        dcc.Interval(
            id='interval-component',
            interval=200,  # in millis
            n_intervals=0
        )
    ])
)

@app.callback(Output('game-state', 'children'),
              [Input('interval-component', 'n_intervals')])
def update_game_state(n):

    f = open(os.getcwd() + "/tester/tmp/current_json.dat", "r")
    json_data = json.loads(f.read())

    # add visualizations
    return [visualize_connections_infected(json_data),
            visualize_round_number(json_data)]


def visualize_round_number(json_data):
    return html.Span('Round: {0}'.format(json_data["round"]), style={'padding': '5px', 'fontSize': '16px'})


def visualize_connections_infected(json_data):
    lat = []
    lon = []
    for city in json_data["cities"].items():
        if "events" in city[1]:
            lat.append(city[1]["latitude"])
            lon.append(city[1]["longitude"])

    data = [dict(
        type='scattergeo',
        locationmode='natural earth',
        lon=lon,
        lat=lat,
        mode='markers',
        marker=dict(
            size=8,
            opacity=0.8,
            symbol='circle',
            line=dict(
                width=1,
                color='rgba(102, 102, 102)'
            ),
        ))]

    layout = dict(
        title='Events',
        colorbar=True,
        geo=dict(
            scope='earth',
            projection='earth',
            showland=True,
            landcolor="rgb(250, 250, 250)",
            subunitcolor="rgb(217, 217, 217)",
            countrycolor="rgb(217, 217, 217)",
            countrywidth=0.5,
            subunitwidth=0.5
        ),
    )

    fig = dict(data=data, layout=layout)

    return dcc.Graph(id='graph', figure=fig)


if __name__ == "__main__":
    app.run_server(debug=False)
