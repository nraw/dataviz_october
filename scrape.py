import requests
from bs4 import BeautifulSoup
import pandas as pd

res = requests.get('https://wheresthejump.com/full-movie-list/')
soup = BeautifulSoup(res.content, 'lxml')

table = soup.find_all('table')[0]
data = pd.read_html(str(table))[0]
data.to_csv('jumpscares.csv')