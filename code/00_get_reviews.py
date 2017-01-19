from bs4 import BeautifulSoup
from urllib.request import urlopen
import sqlite3
import re
import json
import pprint
import logging
import time

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
results = []

# for each biz_id scrape the reviews
for biz_id in biz_ids:

    biz_id = biz_id[0]
    page_start = 0
    retry_count = 0
    prev_reviews_returned = 0

    print('Retrieving Business id: ', biz_id)

    while True:

        print('Retriving from page start = ', page_start)

        # set up url to crawl
        if page_start == 0:
            url = base_url + biz_id
        else:
            url = base_url + biz_id + page_param + str(page_start)

        # get the content
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

            # check if any results are returned
            for review in reviews:
                author = review['author']
                published = review['datePublished']
                rating = review['reviewRating']['ratingValue']
                desc = review['description'].replace('\n', ' ')

                print('Author: %s | Published: %s | Rating %d | Desc: %s' % (author, published, rating, desc))

                record = [author, published, rating, desc]
                results.append(record)

            # commit the results for the business
            conn.executemany('INSERT INTO reviews VALUES (?,?,?,?)', results)
            conn.commit()

            # increment the page and start the next retrieval
            page_start += page_increment

            time.sleep(5)

conn.close()
