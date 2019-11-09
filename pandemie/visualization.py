import json
import os

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
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
            interval=10000,  # in millis
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
    df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/2011_february_us_airport_traffic.csv')
    df.head()

    df['text'] = df['airport'] + '' + df['city'] + ', ' + df['state'] + '' + 'Arrivals: ' + df['cnt'].astype(str)

    scl = [[0, "rgb(5, 10, 172)"], [0.35, "rgb(40, 60, 190)"], [0.5, "rgb(70, 100, 245)"], \
           [0.6, "rgb(90, 120, 245)"], [0.7, "rgb(106, 137, 247)"], [1, "rgb(220, 220, 220)"]]

    data = [dict(
        type='scattergeo',
        locationmode='USA-states',
        lon=df['long'],
        lat=df['lat'],
        text=df['text'],
        mode='markers',
        marker=dict(
            size=8,
            opacity=0.8,
            reversescale=True,
            autocolorscale=False,
            symbol='square',
            line=dict(
                width=1,
                color='rgba(102, 102, 102)'
            ),
            colorscale=scl,
            cmin=0,
            color=df['cnt'],
            cmax=df['cnt'].max(),
            colorbar=dict(
                title="Incoming flightsFebruary 2011"
            )
        ))]

    layout = dict(
        title='Most trafficked US airports<br>(Hover for airport names)',
        colorbar=True,
        geo=dict(
            scope='usa',
            projection=dict(type='albers usa'),
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
