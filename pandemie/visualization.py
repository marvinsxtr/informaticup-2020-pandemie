import datetime

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly
import sys
from dash.dependencies import Input, Output
from pandemie.tester import strategy

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = html.Div(
    html.Div([
        html.H3('Pandemie!'),
        html.Div(id='round'),
        # dcc.Graph(id='live-update-graph'),
        dcc.Interval(
            id='interval-component',
            interval=1000,  # in millis
            n_intervals=0
        )
    ])
)


@app.callback(Output('round', 'children'),
              [Input('interval-component', 'n_intervals')])
def update_metrics(n):

    return [html.Span('Longitude: {0}'.format(1), style={'padding': '5px', 'fontSize': '16px'})]


if __name__ == "__main__":
    app.run_server(debug=True)
