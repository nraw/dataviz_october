import requests
from bs4 import BeautifulSoup
import pandas as pd
import functools
from tqdm import tqdm
import json


def scrape():
    soup = get_main_page()
    jumpscares = get_main_table(soup)
    save_jumpscares(jumpscares)
    good_links = get_links(soup)
    data_details = get_detailed_data(good_links)
    save_data_details(data_details)


def get_main_page():
    res = requests.get('https://wheresthejump.com/full-movie-list/')
    soup = BeautifulSoup(res.content, 'lxml')
    return soup


@functools.lru_cache(600)
def get_soup(link):
    res = requests.get(link)
    soup = BeautifulSoup(res.content, 'lxml')
    return soup


def get_main_table(soup):
    table = soup.find_all('table')[0]
    jumpscares = pd.read_html(str(table))[0]
    return jumpscares


def save_jumpscares(jumpscares):
    jumpscares.to_csv('data/jumpscares.csv')


def get_links(soup):
    all_links = soup.find_all('a')
    pattern = "https://wheresthejump.com/jump-scares"
    good_links = [link.get('href') for link in all_links if pattern in link.get('href')]
    good_links = good_links[1:]
    return good_links


def get_detailed_data(good_links):
    data_details = dict()
    for link in tqdm(good_links):
        soup = get_soup(link)
        movie = soup.find('h1').getText().replace('Jump Scares In', '')
        content_part = soup.find('div', class_='entry-content')
        all_info = content_part.find_all('p')[:-3]
        data_details[movie] = dict()
        data_details[movie]['link'] = link
        data_details[movie]['scare'] = {}
        for info in all_info:
            contents = info.contents
            num_of_contents = len(info.contents)
            if 'Tags:' in str(info):
                field = 'Tags'
                value = [content.getText().strip() for content in contents if 'a href' in str(content)]
                data_details[movie][field] = value
            elif 'peekaboo_content' in str(info):
                scare_contents = info.getText().replace('-', '–').split('–')
                timestamp = scare_contents[0].strip()
                description = scare_contents[1].strip()
                major = '<strong>' in str(contents[0])
                data_details[movie]['scare'][timestamp] = {}
                data_details[movie]['scare'][timestamp]['desc'] = description
                data_details[movie]['scare'][timestamp]['major'] = major
            elif ('imdb.com' in str(info)) |('Rotten Tomatoes:' in str(info)):
                imdb = info.contents[1].strip()
                tomato = info.contents[3].strip()
                data_details[movie]['imdb'] = imdb
                data_details[movie]['tomato'] = tomato
            elif num_of_contents > 1:
                try:
                    field = contents[0].getText().replace(':', '').strip()
                    value = contents[1].strip()
                except:
                    if ':' in info.getText()[1:3]:
                        scare_contents = info.getText().replace('-', '–').split('–')
                        timestamp = scare_contents[0].strip()
                        description = scare_contents[1].strip()
                        major = '<strong>' in str(contents[0])
                        data_details[movie]['scare'][timestamp] = {}
                        data_details[movie]['scare'][timestamp]['desc'] = description
                        data_details[movie]['scare'][timestamp]['major'] = major
                    elif ':' in str(info):
                        field, value = info.getText().split(':')
                    else:
                        print(f'{movie} - nothing found in {str(info)}')
                data_details[movie][field] = value
            elif ':' in info.getText()[1:3]:
                scare_contents = info.getText().replace('-', '–').split('–')
                timestamp = scare_contents[0].strip()
                description = scare_contents[1].strip()
                major = '<strong>' in str(contents[0])
                data_details[movie]['scare'][timestamp] = {}
                data_details[movie]['scare'][timestamp]['desc'] = description
                data_details[movie]['scare'][timestamp]['major'] = major
            else:
                print(f'{movie} - nothing found in {str(info)}')
    return data_details

def add_jump_ratings(data_details, jumpscares):
    for id, row in jumpscares[['link', 'Jump Scare Rating']].iterrows():
        movie = get_movie_by_link(row.link, data_details)
        data_details[movie]['Scare Rating'] = row['Jump Scare Rating']
    return data_details

def get_movie_by_link(link, data_details):
    movie = [movie for movie, data in data_details.items() if data['link'] == link][0]
    return movie


def save_data_details(data_details):
    json.dump(data_details, open('data/data_details.json', 'w'))


def load_data_details():
    data_details = json.load(open('data/data_details.json', 'r'))
