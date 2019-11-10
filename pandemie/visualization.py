import json
import os

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import logging

from plotly.graph_objs.layout.geo import Projection

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.config['suppress_callback_exceptions'] = True
app.title = 'Pandemie!'
app.layout = html.Div(
    html.Div([
        html.H4('Pandemie!'),
        dcc.Dropdown(
            id='data_dropdown',
            options=[
                {'label': 'Visualize one round (current_round)', 'value': 'round'},
                {'label': 'Visualize full game (current_game)', 'value': 'game'},
            ],
            value='round'
        ),
        html.Div(id='game-state'),
    ])
)


@app.callback(
    dash.dependencies.Output('game-state', 'children'),
    [dash.dependencies.Input('data_dropdown', 'value')])
def update_output(value):

    # add visualizations
    path = os.getcwd()
    if value == "round":
        with open(path + "/tester/tmp/current_round.dat", 'r+') as f:
            f.seek(0)
            json_data = json.load(f)
        return visualize_round(json_data)
    else:
        with open(path + "/tester/tmp/current_game.dat", 'r+') as f:
            f.seek(0)
            json_data = json.load(f)
        return visualize_game(json_data)


def visualize_round(json_data):
    return visualize_round_number(json_data)


def visualize_round_number(json_data):
    return html.Span('Round: {0}'.format(json_data["round"]), style={'padding': '5px', 'fontSize': '16px'})


def visualize_game(json_data):
    return [visualize_game_round_count(json_data),
            visualize_game_outcome(json_data)]


def visualize_game_round_count(json_data):
    return html.Span('Rounds: {0}'.format(len(json_data)), style={'padding': '5px', 'fontSize': '16px'})


def visualize_game_outcome(json_data):
    return html.Span('Outcome: {0}'.format(json_data[len(json_data) - 1]["outcome"]), style={'padding': '5px', 'fontSize': '16px'})


def visualize_connections_infected(json_data):
    lat = []
    lon = []
    name = []

    for city in json_data["cities"].items():
        if "events" in city[1]:
            lat.append(city[1]["latitude"])
            lon.append(city[1]["longitude"])
            name.append(city[0])

    fig = go.Figure()

    fig.add_trace(go.Scattergeo(
        locationmode='ISO-3',
        lon=lon,
        lat=lat,
        text=name,
        mode='markers',
        marker=dict(
            size=2,
            color='rgb(255, 0, 0)',
            line=dict(
                width=3,
                color='rgba(68, 68, 68, 0)'
            )
        )))

    flight_paths = []
    left_over_cities = []

    for city in json_data["cities"].items():
        left_over_cities.append(city[0])

    for city in json_data["cities"].items():
        if city[0] in left_over_cities:
            if "events" in city[1]:
                for event in city[1]["events"]:
                    if event["type"] == "outbreak":
                        for connection in city[1]["connections"]:
                            other_city = json_data["cities"][connection]
                            new_connection = dict({"lat1": other_city["latitude"], "lon1": other_city["longitude"],
                                                  "lat2": city[1]["latitude"], "lon2": city[1]["longitude"]})
                            flight_paths.append(new_connection)
            left_over_cities.remove(city[0])

    for i in range(len(flight_paths)):
        fig.add_trace(
            go.Scattergeo(
                locationmode='ISO-3',
                lon=[flight_paths[i]["lon1"], flight_paths[i]["lon2"]],
                lat=[flight_paths[i]["lat1"], flight_paths[i]["lat2"]],
                mode='lines',
                line=dict(width=0.1, color='red'),
                opacity=1,
            )
        )

    fig.update_layout(geo=dict(scope='world',
                               projection=Projection(type="orthographic"),))

    return dcc.Graph(id='graph', figure=fig)


if __name__ == "__main__":
    print("Running on http://127.0.0.1:8050/ ...")
    app.run_server(debug=False)
