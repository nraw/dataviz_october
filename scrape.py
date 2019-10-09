import requests
from bs4 import BeautifulSoup
import pandas as pd
import functools

@functools.lru_cache()
def get_soup(link):
    res = requests.get(link)
    soup = BeautifulSoup(res.content, 'lxml')
    return soup

res = requests.get('https://wheresthejump.com/full-movie-list/')
soup = BeautifulSoup(res.content, 'lxml')

table = soup.find_all('table')[0]
data = pd.read_html(str(table))[0]
data.to_csv('jumpscares.csv')

all_links = soup.find_all('a')  
pattern = "https://wheresthejump.com/jump-scares"    
good_links = [link.get('href') for link in all_links if pattern in link.get('href')]  
good_links = good_links[1:]

for link in good_links:
    res = requests.get(link)
    soup = BeautifulSoup(res.content, 'lxml')
    content_part = soup.find('div', class_='entry-content')
    content_part.find_all('p')[10]
#TODO: make this a nice structure