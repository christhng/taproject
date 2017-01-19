from bs4 import BeautifulSoup
from urllib.request import urlopen
import sqlite3
import re
import json
import pprint

# parameters
# ---------------------------------------------------------
db_path = '../database/jiakbot.db'
base_url = 'https://www.yelp.com.sg/biz/'
page_param = '?start='
page_increment = 20

# connect and write to database
conn = sqlite3.connect(db_path)
c = conn.cursor()

# get the existing biz_ids from database
biz_ids = c.execute('SELECT DISTINCT biz_id FROM businesses;')

# check for whoops

pp = pprint.PrettyPrinter(indent=2)

# for each biz_id scrape the reviews
for biz_id in biz_ids:

    page_start = 0
    biz_id = 'tai-hwa-pork-noodle-singapore'

    # set up url to crawl
    if page_start == 0:
        url = base_url + biz_id
    else:
        url = base_url + biz_id + page_param + str(page_start)

    # get the content
    raw_html = urlopen(url).read()
    soup = BeautifulSoup(raw_html, 'html.parser')

    # check for whoops message (indicates no more reviews)
    whoops_msg = soup.body.findAll(text=re.compile('^Whoops'))

    if len(whoops_msg) > 0:
        break
    else:
        raw_reviews = soup.find_all("script", type="application/ld+json")
        for r in raw_reviews:
            j = json.loads(r.get_text().strip())

            pp.pprint(j)

        break
conn.close()