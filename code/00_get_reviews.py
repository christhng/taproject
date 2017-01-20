from bs4 import BeautifulSoup
from urllib.request import urlopen,urlparse
from urllib.parse import quote

import sqlite3
import re
import json
import pprint
import logging
import time
import configparser

# parameters
# ---------------------------------------------------------

config_file_path='../config_app/app_config.ini'
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
config = configparser.ConfigParser()
config.read(config_file_path)
progress = config['scraper']['progress']
limit = config['scraper']['limit']

# get all biz ids
c.execute('SELECT DISTINCT biz_id FROM businesses LIMIT ' + limit + ' OFFSET ' + progress + ';')
biz_ids = c.fetchall()

# scraping code
# ---------------------------------------------------------
biz_id_count = 0

# for each biz_id scrape the reviews
for biz_id in biz_ids:

    biz_id = biz_id[0]

    page_start = 0
    retry_count = 0
    prev_reviews_returned = 0
    biz_id_count += 1
    print('Retrieving  # %s Business id: %s' %(biz_id_count, biz_id))

    while True:

        results = []
        print('Retrieving from page start = ', page_start)

        # set up url to crawl
        if page_start == 0:
            url = base_url + quote(biz_id)
        else:
            url = base_url + quote(biz_id) + page_param + str(page_start)

        # get the content
        print('Getting from URL: ', url)
        raw_html = urlopen(url, timeout=15).read()
        soup = BeautifulSoup(raw_html, 'html.parser')

        # check for whoops message (indicates no more reviews)
        whoops_msg = soup.body.findAll(text=re.compile('^Whoops'))

        # if whoops message is found, proceed with the next biz_id
        if len(whoops_msg) > 0:
            print('Detected Whoops message')
            time.sleep(10)

            if page_start <= page_increment and retry_count < 3 \
                    and (prev_reviews_returned == 0 or prev_reviews_returned == 20):
                retry_count += 1
                print('Retrying ... Retry count: ', retry_count)
                continue
            else:
                break

        # else get the reviews
        else:
            raw = soup.find_all("script", type="application/ld+json")
            parsed = json.loads(raw[0].get_text().strip())
            reviews = parsed['review']

            prev_reviews_returned = len(reviews)
            print('Previous reviews returned: ',prev_reviews_returned)

            # parse each review text
            for review in reviews:
                author = review['author']
                published = review['datePublished']
                rating = review['reviewRating']['ratingValue']
                desc = review['description'].replace('\n', ' ')

                print('Author: %s | Published: %s | Rating %d | Desc: %s' % (author, published, rating, desc))

                record = [biz_id, author, published, rating, desc]
                results.append(record)

            # commit the results for the business
            c.executemany('INSERT INTO reviews VALUES (?,?,?,?,?)', results)
            conn.commit()

            # increment the page and start the next retrieval
            page_start += page_increment

            time.sleep(15)

            # break prev_reviews are already less than 20
            # no need to try next page
            if prev_reviews_returned < 20: break



conn.close()

# Writing our configuration file to 'example.cfg'
with open(config_file_path, 'w') as configfile:
    v = int(progress)+int(limit)
    config.set('scraper','progress',str(v))
    config.write(configfile)
