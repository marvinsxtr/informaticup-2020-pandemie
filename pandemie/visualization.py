"""
This file contains everything needed to visualize games or individual rounds using the dash framework with plotly.
"""
import sys

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
import logging
import pandemie.preprocessing as pre

from plotly.graph_objs.layout.geo import Projection

# displayed lists of graphs/plots
visualized_rounds = []
visualized_game = []

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
            options=pre.option_labels,
            value='game',
        ),
        html.Div(id='game-state'),
    ])
)


@app.callback(
    dash.dependencies.Output('game-state', 'children'),
    [dash.dependencies.Input('data_dropdown', 'value')])
def update_output(value):
    # add visualizations
    if value is None:
        return
    if value == "game":
        return visualized_game
    else:
        number = int(''.join(filter(str.isdigit, value)))
        return visualized_rounds[number - 1]


def visualize_round(number):
    """
    This function visualizes a round of the pandemie game. The returned list is displayed as a column in dash.
    :return: list of visualizations
    """
    return [visualize_round_number(number),
            visualize_round_connections_infected(number),
            visualize_round_pathogens_pie(number)]


def visualize_round_number(number):
    # displays the visualized round number
    return html.Span('Round: {0}'.format(number + 1), style={'padding': '5px', 'fontSize': '16px'})


def visualize_round_connections_infected(number):
    # city positions
    lon = pre.round_visualizations[number]["lon"]
    lat = pre.round_visualizations[number]["lat"]
    text = pre.round_visualizations[number]["name"]

    fig = go.Figure()

    fig.add_trace(go.Scattergeo(
        locationmode='ISO-3',
        showlegend=False,
        lon=lon,
        lat=lat,
        text=text,
        mode='markers',
        marker=dict(
            size=4,
            color='rgb(255, 0, 0)',
            line=dict(
                width=3,
                color='rgba(68, 68, 68, 0)'
            )
        )))

    # flight paths
    """
    flight_paths = pre.round_visualizations[number]["flight_paths"]
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
    """
    fig.update_layout(geo=dict(scope='world', projection=Projection(type="orthographic"), ))
    fig.update_layout(title='Outbreaks')

    return dcc.Graph(id='connections', figure=fig)


def visualize_round_pathogens_pie(number):
    # displays encountered pathogens by city in percent
    counts = pre.round_visualizations[number]["counts"]
    names = pre.round_visualizations[number]["names"]

    fig = go.Figure(data=[go.Pie(labels=names, values=counts)])
    fig.update_layout(title='Pathogens by affected cities')

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
    # prints round count of a game
    return html.Span('Rounds: {0}'.format(len(pre.round_names)), style={'padding': '5px', 'fontSize': '16px'})


def visualize_game_outcome():
    # prints the outcome
    outcome = pre.game_visualizations["outcome"]

    return html.Span('Outcome: {0}'.format(outcome), style={'padding': '5px', 'fontSize': '16px'})


def visualize_game_population():
    # visualizes the population development in a game
    x_rounds = pre.game_visualizations["x_rounds"]
    y_population = pre.game_visualizations["y_population"]

    fig = go.Figure(go.Scatter(x=x_rounds, y=y_population, mode='lines+markers'))
    fig.update_layout(title='World Population')

    return html.Div([dcc.Graph(id='population', figure=fig)])


def visualize_pathogens_in_full_game():
    # visualizes a list of all pathogens appeared in the game
    pathogens = pre.game_visualizations["pathogens"]

    return html.Span('All pathogens in game: ' + str(pathogens), style={'padding': '5px', 'fontSize': '16px'})


if __name__ == "__main__":
    print("Started pre-processing")
    pre.preprocess()

    print("Started generating visualizations")
    for round_number in range(len(pre.round_names)):
        visualized_rounds.append(visualize_round(round_number))
        sys.stdout.write("\r \rVisualized round %d / %d" % (round_number + 1, len(pre.round_names)))
        sys.stdout.flush()
    sys.stdout.write("\n")

    print("Start generating game visualization")
    visualized_game = visualize_game()

    print("Running on http://127.0.0.1:8050/...")
    app.run_server(debug=False)
