import requests
from bs4 import BeautifulSoup

def fetch_operators():
    url = "https://prts.wiki/w/%E5%89%A7%E6%83%85%E4%B8%80%E8%A7%88"
    response = requests.get(url)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')

    