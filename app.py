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
from src.markdown_info import get_markdown_info

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
fields = ['imdb', 'tomato', 'Jump Scares', 'Major Jump Scares', 'Minor Jump Scares', 'Runtime', 'Scare Rating', 'is_instance']


def serve_layout():
    session_id = str(uuid.uuid4())
    return html.Div([
        html.Div([
        html.Div(session_id, id='session-id', style={'display': 'none'}),
        html.Div([
            dcc.Graph(id='main-graph',style={'height': '98vh'}),
        ],
            style={'display': 'block', 'backgroundColor': 'black'},
            id='charts-div'
        )],
            className='nine columns',
        style={'backgroundColor': 'black'}
    ),
        html.Div([
            html.Label(['Node:',
                dcc.Dropdown(
                    options=[{'label': node, 'value': node} for node in G],
                    searchable=True,
                    id='node_input'
                )
            ]),
            html.Label(['Size:',
                dcc.Dropdown(
                    options=[{'label': field, 'value': field} for field in fields],
                    searchable=True,
                    id='dim0',
                    value='imdb'
                )
           ]),
            html.Label(['Color:',
                        dcc.Dropdown(
                            options=[{'label': field, 'value': field} for field in fields],
                            searchable=True,
                            id='dim1',
                            value='is_instance'
                        )
                        ]),
            html.Label(['x:',
                        dcc.Dropdown(
                            options=[{'label': field, 'value': field} for field in fields],
                            searchable=True,
                            id='dim2',
                        )
                        ]),
            html.Label(['y:',
                        dcc.Dropdown(
                            options=[{'label': field, 'value': field} for field in fields],
                            searchable=True,
                            id='dim3',
                        )
                        ]),
            dcc.Markdown(id='markdown_info', style={"white-space": "pre", "overflow-x": "scroll", "overflow-y": "scroll"}),
        ], className='three columns', style={'height': '98vh'})
    ], className='row')

app.layout = serve_layout


@app.callback(
    [Output('main-graph', 'figure'),
     Output('markdown_info', 'children')],
    [Input('main-graph', 'clickData'),
     Input('node_input', 'value'),
     Input('dim0', 'value'),
     Input('dim1', 'value'),
     Input('dim2', 'value'),
     Input('dim3', 'value')])
def update_graph(click_data, node_input, dim0, dim1, dim2, dim3):
    ctx = dash.callback_context
    if not ctx.triggered:
        node = None
    else:
        trigger = ctx.triggered[0]['prop_id']
        if trigger == 'node_input.value':
            node = node_input
        elif trigger == 'main-graph.clickData':
            node = click_data['points'][0]['text']
        else:
            node = None

    if node in ['tag', 'director', 'movie']:  # Plotly bug?
        node = None
    if dim2 is None or dim3 is None:
        dims = [dim0, dim1]
    else:
        dims = [dim0, dim1, dim2, dim3]
    fig = plot_G(G, dims, node, auto_open=False)
    fig.update_layout({'uirevision': True})
    markdown_info = get_markdown_info(G, node)
    # print(fig)
    return [fig, markdown_info]


if __name__ == '__main__':
    app.run_server(debug=True)
