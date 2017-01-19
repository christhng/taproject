from bs4 import BeautifulSoup
from urllib.request import urlopen
import sqlite3
import re
import json
import pprint
import logging

# parameters
# ---------------------------------------------------------
db_path = '../database/jiakbot.db'
base_url = 'https://www.yelp.com.sg/biz/'
page_param = '?start='
page_increment = 20

# set up logger and prettyprinter
logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.WARNING)

pp = pprint.PrettyPrinter(indent=2)

# connect and write to database
conn = sqlite3.connect(db_path)
c = conn.cursor()

# get the existing biz_ids from database
biz_ids = c.execute('SELECT DISTINCT biz_id FROM businesses;')

# scraping code
# ---------------------------------------------------------
proceed = True

# for each biz_id scrape the reviews
for biz_id in biz_ids:

    page_start = 0
    biz_id = 'tai-hwa-pork-noodle-singapore'

    while proceed:

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

        # if whoops message is found, proceed with the next biz_id
        if len(whoops_msg) > 0:
            break

        # else get the reviews
        else:
            raw_reviews = soup.find_all("script", type="application/ld+json")
            for r in raw_reviews:
                j = json.loads(r.get_text().strip())

                pp.pprint(j)


        break
conn.close()