import configparser # for reading ini files. https://docs.python.org/3/library/configparser.html
import rauth    # for oauth
import pprint # for pretty printing in console
import json

# parameters
# -------------------------------------------------------------------
term = ['food','restaurants'] # indicates what to search for
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

# Read in the config in the auth files
config = configparser.ConfigParser()
config.read(config_file_path)

consumer_key = config['yelp']['consumer_key']
consumer_secret = config['yelp']['consumer_secret']
access_token_key = config['yelp']['access_token_key']
access_token_secret = config['yelp']['access_token_secret']

client_id=config['yelp']['client_id']
client_secret=config['yelp']['client_secret']

service = rauth.OAuth2Service(
    client_id=client_id,
    client_secret=client_secret,
    access_token_url='https://api.yelp.com/oauth2/token'
)

# get the access token
raw_atoken = service.get_raw_access_token()
raw_atoken_dict = raw_atoken.json()

access_token = raw_atoken_dict['access_token']
token_type = raw_atoken_dict['token_type']

def oauth_decode(data):
    new_data = data.decode("utf-8", "strict")
    return json.loads(new_data)

data = {'grant_type': 'client_credentials',
        'client_id': access_token_key,
        'client_secret': access_token_secret}

session = service.get_auth_session(data=data, decoder=oauth_decode)

request = session.get('http://api.yelp.com/v3/businesses/long-ji-zi-char-singapore/reviews')

data = request.json()
pp = pprint.PrettyPrinter(indent=2)
pp.pprint(data)

# another way for oauth2 using requests
# import requests
#
# app_id = 'client_id'
# app_secret = 'client_secret'
# data = {'grant_type': 'client_credentials',
#         'client_id': app_id,
#         'client_secret': app_secret}
# token = requests.post('https://api.yelp.com/oauth2/token', data=data)
# access_token = token.json()['access_token']
# url = 'https://api.yelp.com/v3/businesses/search'
# headers = {'Authorization': 'bearer %s' % access_token}
# params = {'location': 'San Bruno',
#           'term': 'Japanese Restaurant',
#           'pricing_filter': '1, 2',
#           'sort_by': 'rating'
#          }
#
# resp = requests.get(url=url, params=params, headers=headers)

# pprint.pprint(resp.json()['businesses'])