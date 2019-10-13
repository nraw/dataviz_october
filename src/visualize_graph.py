import numpy as np
import pandas as pd
import plotly.offline as plt
import plotly.graph_objs as go
import networkx as nx
from tqdm import tqdm
import functools
tqdm.pandas()

mck_palette = ['#FAA082', '#AFC3FF', '#E5546C', '#034B6F', '#8C5AC8', '#E6A0C8', '#027AB1', '#39BDF3', '#71D2F1', '#3C96B4', '#AAE6F0']

mck_palette_mapping = {
    "movie": mck_palette[4],
    "person": mck_palette[5],
    "tag": mck_palette[3]
}


def plot_G(G, dims=None, node=None, auto_open=True):
    df_pos = get_positions(G, dims)
    node_trace = get_node_trace(G, df_pos, dims, node)
    edge_trace = get_edge_trace(G, df_pos)
    fig = get_figure(edge_trace, node_trace)
    # fig.update_layout(images = images)
    if auto_open:
        plt.plot(fig, auto_open=True)
    return fig


def get_positions(G, dims):
    if len(dims) == 4:
        pos = [[node, data[dims[2]], data[dims[3]]] for node, data in G.nodes(data=True)]
        df_pos = pd.DataFrame(pos, columns=['index', 'x','y'])
    else:
        df_pos = get_algo_positions(G)
    return df_pos


@functools.lru_cache()
def get_algo_positions(G):
    # pos=nx.kamada_kawai_layout(G) # IS KAWAII
    # pos = nx.shell_layout(G) # IS A CIRCLE
    # pos = nx.spring_layout(G, k=0.3, seed=2)  # THIS ONE LOOKS PROMISING
    pos = nx.spring_layout(G)  # THIS ONE LOOKS PROMISING
    # pos = nx.spring_layout(G, 3) # THIS ONE LOOKS PROMISING
    # pos = nx.spectral_layout(G) # LOL WAT IS DIS
    df_pos = pd.DataFrame(pos, index=['x', 'y']).T.reset_index()
    return df_pos


def get_node_trace(G, df_pos, dims, node=None):
    max_size = 40
    default_size = 20
    node_trace = go.Scatter(
        x=[],
        y=[],
        text=[],
        mode='markers',
        hoverinfo='text',
        marker=dict(
            showscale=True,
            opacity=0.8,
            colorscale='YlGnBu',
            reversescale=True,
            color=[],
            size=20,
            colorbar=dict(
                thickness=15,
                # title='Has shared any file in March 2019',
                xanchor='left',
                titleside='right'
            ),
            line=dict(width=2)))
    df_nodes = pd.DataFrame(G.nodes(data=True), columns=['n', 'data'])
    df_nodes[dims[0]] = df_nodes['data'].apply(lambda x: x[dims[0]])
    df_nodes['norm_size'] = normalize(df_nodes[dims[0]])
    df_nodes['bubble_size'] = df_nodes['norm_size'].apply(lambda x: get_bubble_size(x, max_size, default_size))
    df_nodes[dims[1]] = df_nodes['data'].apply(lambda x: x[dims[1]])
    df_nodes['color'] = df_nodes[dims[1]].astype('category').cat.codes.apply(lambda x: mck_palette[x%11])
    df_nodes = df_nodes.merge(df_pos, left_on='n', right_on='index')
    # df_nodes = df_nodes.merge(tb.fillna(0), how='left', left_on='n', right_on='fmno')
    node_trace['x'] = df_nodes['x'].to_list()
    node_trace['y'] = df_nodes['y'].to_list()
    node_trace['text'] = df_nodes['n'].to_list()
    node_trace['marker']['color'] = df_nodes['color'].to_list()
    node_trace['marker']['size'] = df_nodes['bubble_size'].to_list()

    # images = df_nodes[df_nodes.is_instance == 'movie'].apply(lambda x: create_image_layout(x.img_url, x.x, x.y, x.bubble_size), axis=1).to_list()
    if node:
        node_type = G.node[node]['is_instance']
        neighbors = list(nx.neighbors(G, node))
        extra_neighbors = [list(nx.neighbors(G, node)) for node in neighbors]
        filtered_extra = [n for ns in extra_neighbors for n in ns if G.node[n]['is_instance'] != node_type]
        selected_few = neighbors + filtered_extra + [node]
        node_trace['marker']['opacity'] = df_nodes.n.apply(lambda x: (x in selected_few) * 0.7 + 0.1).to_list()
    return node_trace


def normalize(x):
    normalized = (x - min(x))/(max(x) - min(x))
    return normalized


def get_bubble_size(x, max_size, default_size, power_skew = 4):
    if not np.isnan(x):
        bubble_size = x**power_skew * max_size
    else:
        bubble_size = default_size
    return bubble_size


def get_edge_trace(g, df_pos):
    edge_trace = go.Scatter(
        x=[],
        y=[],
        line=dict(width=0.5, color='#888'),
        hoverinfo='text',
        mode='lines')
    df_edges = pd.DataFrame(g.edges(data=True), columns=['a', 'b', 'connection'])
    df_edges['connection'] = df_edges['connection'].apply(lambda x: x['connection'])
    df_edges = df_edges.merge(df_pos, left_on='a', right_on='index', suffixes=('o', 'a')).merge(df_pos, left_on='b', right_on='index', suffixes=('a', 'b'))
    x = df_edges.apply(lambda o: tuple([o.xa, o.xb, None]), axis=1)
    x = [single_x for tuple_x in x for single_x in tuple_x]
    y = df_edges.apply(lambda o: tuple([o.ya, o.yb, None]), axis=1)
    y = [single_y for tuple_y in y for single_y in tuple_y]
    edge_trace['x'] = x
    edge_trace['y'] = y
    edge_trace['text'] = list(df_edges['connection'])
    return edge_trace


def get_figure(edge_trace, node_trace):
    fig = go.Figure(data=[edge_trace, node_trace],
                    layout=go.Layout(
                        # title=f'<br>{target} {practice_function}',
                        paper_bgcolor='black',
                        plot_bgcolor='black',
                        titlefont=dict(size=16),
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=20, l=5, r=5, t=40),
                        # annotations=[dict(
                        #     text="Python code: <a href='https://plot.ly/ipython-notebooks/network-graphs/'> https://plot.ly/ipython-notebooks/network-graphs/</a>",
                        #     showarrow=False,
                        #     xref="paper", yref="paper",
                        #     x=0.005, y=-0.002 ) ],
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)))
    return fig


# plot_G(H, 'Texas Chainsaw 3D (2013)')
# plot_G(G, dims)
