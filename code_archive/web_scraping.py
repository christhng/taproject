from bs4 import BeautifulSoup
import urllib
from urllib.request import urlopen

r = urlopen('https://www.yelp.com.sg/biz/tai-hwa-pork-noodle-singapore').read()
soup = BeautifulSoup(r,'html.parser')

print(type(soup))

letters = soup.find_all("script", type="application/ld+json")

print(letters)


