import configparser # for reading ini files. https://docs.python.org/3/library/configparser.html
import pprint # for pretty printing in console
import json # for processing json stuff
import requests

# parameters
# -------------------------------------------------------------------
terms = ['food'] # ,restaurants indicates what to search for
locations = ['raffles place'] # indicates the neighbourhood to search
lat = [] # to be used if locations are not specified
lng = [] # to be used if locations are not specified
radius = 10000 # radius in meters (max is 40000)
limit = 50 # number of results to return with each call. to be used with offset.
offset = 0 # Offset the list of returned business results by this amount. max business from endpoint is 1000

# reference here: https://www.yelp.com.sg/developers/documentation/v3/business_search

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
for term in terms:

    for location in locations:

        # set the parameters
        params = {}
        params['term'] = term
        params['location'] = location
        params['limit'] = 10

        # get the response
        response = requests.get(url=url, params=params, headers=headers)
        parsed = response.json()
        businesses = parsed['businesses']

        # get each business
        for biz in businesses:
            biz_id = biz['id']
            biz_name = biz['name']
            biz_categories = "|".join([d['title'] for d in biz['categories']])
            biz_rating = biz['rating']
            biz_lat = biz['coordinates']['latitude']
            biz_lng = biz['coordinates']['longitude']

            print('biz id:%s\nname: %s\n%s\n%s\n%s\n%s' % (biz_id,biz_name,biz_categories,biz_rating,biz_lat,biz_lng))
            print('---------------------------------------')

            # append to list

            # get next off set record

# write to csv