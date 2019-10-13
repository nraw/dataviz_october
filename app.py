import base64
import io
import uuid
from textwrap import wrap

import dash
import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import pandas as pd
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State
from flask_caching import Cache
from src.graph import get_graph
from src.visualize_graph import plot_G

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css', "https://codepen.io/chriddyp/pen/brPBPO.css"]  # dash and loading spinner css

# mck_palette = ['#034B6F', '#027AB1', '#39BDF3', '#71D2F1', '#AFC3FF', '#3C96B4', '#AAE6F0',
#                '#8C5AC8', '#E6A0C8', '#E5546C', '#FAA082']
mck_palette = ['#034B6F', '#8C5AC8', '#E6A0C8', '#E5546C', '#FAA082', '#AFC3FF', '#027AB1', '#39BDF3', '#71D2F1', '#3C96B4', '#AAE6F0']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
cache = Cache(app.server, config={
    'CACHE_TYPE': 'redis',
    # Note that filesystem cache doesn't work on systems with ephemeral
    # filesystems like Heroku.
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': 'cache-directory',

    # should be equal to maximum number of users on the app at a single time
    # higher numbers will store more data in the filesystem / redis cache
    'CACHE_THRESHOLD': 200
})

G = get_graph()


def serve_layout():
    session_id = str(uuid.uuid4())
    return html.Div([
        html.Div(session_id, id='session-id', style={'display': 'none'}),
        html.Div([
            dcc.Graph(id='main-graph',style={'height':'100vh'}),
        ],
            style={'display': 'block'},
            id='charts-div'
        ),
    ])


app.layout = serve_layout


@app.callback(
    [Output('main-graph', 'figure')],
    [Input('main-graph', 'clickData')])
def update_graph(click_data):
    print(click_data)
    if click_data:
        node = click_data['points'][0]['text']
    else:
        node = None
    dims = ['imdb', 'is_instance']
    fig = plot_G(G, dims, node, auto_open=False)
    fig.update_layout({'uirevision': True})
    print(fig)
    return [fig]


if __name__ == '__main__':
    app.run_server(debug=True)
