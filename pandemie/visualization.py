"""
This file contains everything needed to visualize games or individual rounds using the dash framework with plotly.
"""

import json
import os
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
import logging

from plotly.graph_objs.layout.geo import Projection

options = [{'label': 'Visualize full game', 'value': 'game'}]
round_names = sorted(os.listdir(os.getcwd() + "/tester/tmp/"), key=lambda item: int(''.join(filter(str.isdigit, item))))


def get_rounds():
    for round_name in round_names:
        options.append({'label': 'Visualize {0}'.format(round_name), 'value': round_name})


log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.config['suppress_callback_exceptions'] = True
app.title = 'Pandemie!'
app.layout = html.Div(
    html.Div([
        html.Center(html.H4('Pandemie!'), ),
        dcc.Dropdown(
            id='data_dropdown',
            options=options,
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
    if value is None:
        return
    if value == "game":
        return visualize_game()
    else:
        with open(path + "/tester/tmp/{0}".format(value), 'r+') as f:
            f.seek(0)
            json_data = json.load(f)
        return visualize_round(json_data)


def visualize_round(json_data):
    """
    This function visualizes a round of the pandemie game. The returned list is displayed as a column in dash.
    :param json_data: round data
    :return: list of visualizations
    """
    return [visualize_round_number(json_data),
            visualize_round_connections_infected(json_data),
            visualize_round_pathogens_pie(json_data)]


def visualize_round_number(json_data):
    return html.Span('Round: {0}'.format(json_data["round"]), style={'padding': '5px', 'fontSize': '16px'})


def visualize_round_connections_infected(json_data):
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
        showlegend=False,
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
                showlegend=False,
                lon=[flight_paths[i]["lon1"], flight_paths[i]["lon2"]],
                lat=[flight_paths[i]["lat1"], flight_paths[i]["lat2"]],
                mode='lines',
                line=dict(width=0.1, color='red'),
                opacity=1,
            )
        )

    fig.update_layout(geo=dict(scope='world',
                               projection=Projection(type="orthographic"), ))

    return dcc.Graph(id='connections', figure=fig)


def visualize_round_pathogens_pie(json_data):
    labels = []
    values = {}

    for city in json_data["cities"].items():
        if "events" in city[1]:
            for event in city[1]["events"]:
                if event["type"] == "outbreak":
                    pathogen = event["pathogen"]
                    if pathogen not in labels:
                        labels.append(pathogen["name"])
                        if not pathogen["name"] in values:
                            values[pathogen["name"]] = 1
                        else:
                            values[pathogen["name"]] += 1

    counts = []
    names = []
    for key, value in (values.items()):
        names.append(key)
        counts.append(value)

    fig = go.Figure(data=[go.Pie(labels=names, values=counts)])

    return html.Div([dcc.Graph(id='pathogen_pie', figure=fig)])


def visualize_game():
    """
    This function visualizes a complete pandemie game by iterating over the json for each round.
    :return: list of visualizations
    """
    return [visualize_game_round_count(),
            visualize_game_outcome(),
            visualize_game_population(), visualize_pathogens_in_full_game()]


def visualize_game_round_count():
    return html.Span('Rounds: {0}'.format(len(round_names)), style={'padding': '5px', 'fontSize': '16px'})


def visualize_game_outcome():
    path = os.getcwd()
    last = round_names[len(round_names) - 1]
    with open(path + "/tester/tmp/{0}".format(last), 'r+') as f:
        f.seek(0)
        json_data = json.load(f)
    return html.Span('Outcome: {0}'.format(json_data["outcome"]),
                     style={'padding': '5px', 'fontSize': '16px'})


def visualize_game_population():
    path = os.getcwd()
    last = round_names[len(round_names) - 1]
    with open(path + "/tester/tmp/{0}".format(last), 'r+') as f:
        f.seek(0)
        json_data = json.load(f)

    y_population = []
    x_rounds = []
    tmp = []

    for r in range(json_data["round"]):
        x_rounds.append(r)
        tmp.append(r)

    for round in round_names:
        path = os.getcwd()
        with open(path + "/tester/tmp/{0}".format(round), 'r+') as f:
            f.seek(0)
            game = json.load(f)
            if game["round"] in tmp:
                p = 0
                for city in game["cities"].items():
                    p += city[1]["population"]
                y_population.append(p)
                tmp.remove(game["round"])

    fig = go.Figure(go.Scatter(x=x_rounds, y=y_population, mode='lines+markers'))

    fig.update_layout(title='World Population')

    return html.Div([dcc.Graph(id='population', figure=fig)])


def visualize_pathogens_in_full_game():
    # visualizes a list of all pathogens appeared in the game
    pathogens = []
    path = os.getcwd()
    last = round_names[len(round_names) - 1]
    with open(path + "/tester/tmp/{0}".format(last), 'r+') as f:
        f.seek(0)
        json_data = json.load(f)

    x_rounds = []
    for r in range(json_data["round"]):
        x_rounds.append(r)

    for round in round_names:
        with open(path + "/tester/tmp/{0}".format(round), 'r+') as f:
            f.seek(0)
            game = json.load(f)

            for city in game["cities"].items():
                if "events" in city[1]:
                    for event in city[1]["events"]:
                        if event["type"] == "outbreak":
                            pathogen = event["pathogen"]
                            if pathogen not in pathogens:
                                pathogens.append(pathogen["name"])

    pathogens = list(set(pathogens))

    return html.Span('All pathogens in game: ' + str(pathogens),
                     style={'padding': '5px', 'fontSize': '16px'})


if __name__ == "__main__":
    get_rounds()
    # todo: make visualization more efficient by pre-computing data here
    print("Running on http://127.0.0.1:8050/...")
    app.run_server(debug=False)
