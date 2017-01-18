import configparser # for reading ini files. https://docs.python.org/3/library/configparser.html
import pprint # for pretty printing in console
import json # for processing json stuff
import requests # for firing off requests
import time # for rate limiting
import logging # for messages. better than print.
import sqlite3 # for writing records to db

# parameters
# -------------------------------------------------------------------
terms = ['food','restaurants'] # ,restaurants indicates what to search for
locations = ['dhoby ghaut'] #city hall, raffles place, bras basah, dhoby ghaut # indicates the neighbourhood to search
lat = [] # to be used if locations are not specified
lng = [] # to be used if locations are not specified
radius = 10000 # radius in meters (max is 40000)
limit = 50 # number of results to return with each call. to be used with offset.

# reference here: https://www.yelp.com.sg/developers/documentation/v3/business_search

# for keeping track of the records received
max_records = 1000
total_records_retrieved = 0

# set up logger
logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.WARNING)

# file locations
# -------------------------------------------------------------------
business_id_file_path = '../data/business_ids'
config_file_path = '../config_auth/auth.ini'

# main code
# -------------------------------------------------------------------

# Read in the config in the auth files
config = configparser.ConfigParser()
config.read(config_file_path)

client_id=config['yelp']['client_id']
client_secret=config['yelp']['client_secret']

# declare pretty printer for pretty printing the results
pp = pprint.PrettyPrinter()

# get access token
data = {'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret}

token = requests.post('https://api.yelp.com/oauth2/token', data=data)
access_token = token.json()['access_token']

# specify the endpoint url and headers
url = 'https://api.yelp.com/v3/businesses/search'
headers = {'Authorization': 'bearer %s' % access_token}

# search parameters for each term ... search each location
results = []

for term in terms:

    for location in locations:

        print('Retrieving ... %s | %s' % (term, location))

        curr_count = 0
        offset = 0

        # retrieves records until the maximum we specify earlier
        while curr_count < max_records:

            # set the parameters
            params = {}
            params['term'] = term
            params['location'] = location
            params['limit'] = limit
            params['offset'] = offset

            # get the response
            response = requests.get(url=url, params=params, headers=headers)
            parsed = response.json()
            available_records = parsed['total']
            businesses = parsed['businesses']

            logger.info('Requesting for ' + str(params))
            logger.info('Available records for biz: ' + str(available_records))
            logger.info('Raw response ' + str(parsed))

            # if available is less than max, set it to available
            if available_records < max_records:
                max_records = available_records

            # get each business
            for biz in businesses:
                biz_id = biz['id']
                biz_name = biz['name']
                biz_categories = "|".join([d['title'] for d in biz['categories']])
                biz_rating = biz['rating']
                biz_lat = biz['coordinates']['latitude']
                biz_lng = biz['coordinates']['longitude']

                logger.debug('biz id:%s\nname: %s\n%s\n%s\n%s\n%s' % (biz_id,biz_name,biz_categories,biz_rating,biz_lat,biz_lng))

                # append to list
                record = [biz_id,biz_name,biz_categories,biz_rating,biz_lat,biz_lng]
                results.append(record)

                # increment records received count
                curr_count += 1
                total_records_retrieved += 1

            # get next off set record
            offset = offset + limit

            # rate limit the api calls
            print('Records retrieved to date :', total_records_retrieved)

            time.sleep(1)

        time.sleep(30)

    time.sleep(30)

# connect and write to database
conn = sqlite3.connect('../database/jiakbot.db')
c = conn.cursor()

# prepare and execute statement
for record in results:
    var_str = ', '.join('?' * len(record))
    query_str = 'INSERT INTO businesses VALUES (%s);' % var_str
    c.execute(query_str,record)

conn.commit()
conn.close()

