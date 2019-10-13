import networkx as nx
import numpy as np
import pandas as pd
import json
import re


def get_graph():
    data_details = load_details()
    directors_connections_all = get_directors(data_details)
    tags_connections_raw = get_tags(data_details)
    tags_connections = fix_tags(tags_connections_raw)
    concatenated_connections = concatenate_connections(directors_connections_all, tags_connections)
    graph_df = get_graph_df(concatenated_connections)
    G = create_graph(graph_df)
    G = mark_nodes(G, data_details, graph_df)
    return G


def load_details():
    data_details = json.load(open('data/data_details.json', 'r'))
    data_details = {k.replace('Jump Scares In ', ''):v for k,v in data_details.items()}
    return data_details

def get_directors(data_details):
    director_connections = [[movie, data_details[movie]['Director'], 'director'] for movie in data_details if 'Director' in data_details[movie].keys()]
    directors_connections = [[[movie, director.strip(), 'director'] for director in data_details[movie]['Directors'].split(',')] for movie in data_details if 'Directors' in data_details[movie].keys()]
    directors_connections = [director_connection for movie_directors in directors_connections for director_connection in movie_directors]
    directors_connections_all = director_connections + directors_connections
    return directors_connections_all


def get_tags(data_details):
    tags_connections_raw = [[[movie,tag, 'tag'] for tag in data_details[movie]['Tags']] for movie in data_details if 'Tags' in data_details[movie].keys()]
    tags_connections_raw = [tag_connections for movie_directors in tags_connections_raw for tag_connections in movie_directors]
    return tags_connections_raw


def fix_tags(tags_connections_raw):
    tags_connections = [[movie, fix_tag(tag), connection] for movie, tag, connection in tags_connections_raw]
    return tags_connections


def fix_tag(tag):
    if (tag == 'Religion & the Occult') | (tag == 'Religion / The Occult'):
        tag = 'Religion & The Occult'
    elif tag == 'Montsers & Mutants':
        tag = 'Monsters & Mutants'
    elif tag == 'Creepy Child':
        tag = 'Creepy Children'
    return tag


def concatenate_connections(directors_connections_all, tags_connections):
    concatenated_connections = directors_connections_all + tags_connections
    return concatenated_connections


def get_graph_df(concatenated_connections):
    connections_columns = ['subject', 'object', 'connection']
    graph_df = pd.DataFrame(concatenated_connections, columns=connections_columns)
    return graph_df


def create_graph(graph_df):
    G = nx.from_pandas_edgelist(graph_df, 'subject','object','connection')
    return G


def mark_nodes(G, data_details, graph_df):
    mark_movies(G, data_details)
    mark_directors(G, graph_df)
    mark_tags(G, graph_df)
    fields = ['imdb', 'tomato', 'Jump Scares', 'Major Jump Scares', 'Minor Jump Scares', 'Runtime', 'Scare Rating']
    mark_all_average_scores(G, fields)
    return G


def mark_movies(G, data_details):
    for movie, infos in data_details.items():
        G.node[movie]['is_instance'] = 'movie'
        for info_name, info_value in infos.items():
            info_name, info_value = fix_info(info_name, info_value)
            if info_name == 'Jump Scares':
                fix_jump_scares(G, movie, info_value)
            else:
                G.node[movie][info_name] = info_value


def fix_info(info_name, info_value):
    if info_name == 'imdb':
        info_value = imdb_score_to_float(info_value)
    elif info_name == 'tomato':
        if info_value == 'N/A':
            info_value = np.nan
        else:
            info_value = float(info_value.replace('%',''))/100
    elif info_name == 'Runtime':
        pattern = '\d+'
        info_value = re.findall(pattern, info_value)[0]
        info_value = float(info_value)
    return info_name, info_value


def imdb_score_to_float(imdb_score):
    # size = float(df_nodes['data'][0]['imdb'].replace('/10',''))/10
    imdb_score = imdb_score.replace('/10', '')
    size = float(imdb_score) / 10
    return size


def fix_jump_scares(G, movie, info_value):
    both, major, _, minor, _ = info_value.split()
    major = major.replace('(', '')
    G.node[movie]['Jump Scares'] = int(both)
    G.node[movie]['Major Jump Scares'] = int(major)
    G.node[movie]['Minor Jump Scares'] = int(minor)


def mark_directors(G, graph_df):
    directors = graph_df[graph_df.connection == 'director']['object'].drop_duplicates()
    for director in directors:
        G.node[director]['is_instance'] = 'person'


def mark_tags(G, graph_df):
    tags = graph_df[graph_df.connection == 'tag']['object'].drop_duplicates()
    for tag in tags:
        G.node[tag]['is_instance'] = 'tag'


def mark_all_average_scores(G, fields):
    for field in fields:
        mark_average_scores(G, field)


def mark_average_scores(G, field):
    nodes = [node for node, data in G.nodes(data=True) if data['is_instance'] in ['person', 'tag']]
    average_scores = {node: get_average_score([movie for node, movie in G.edges(node)], G, field) for node in nodes}
    for node, score in average_scores.items():
        G.node[node][field] = score


def get_average_score(movies, G, field):
    imdb_score = np.nanmean([G.nodes[node][field] for node in movies if field in G.nodes[node].keys()])
    imdb_score = np.round(imdb_score, 2)
    return imdb_score


def _filter_nodes(self, key, value):
    subgraph = [node for node, data in self.nodes(data=True) if data[key] == value]
    return subgraph


# G = get_graph()