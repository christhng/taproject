import configparser # for reading ini files. https://docs.python.org/3/library/configparser.html
import requests
import json,pprint
from urllib.parse import parse_qs, urlencode, urlparse

config_file_path = '../config_auth/auth.ini'

# Read in the config in the auth files
config = configparser.ConfigParser()
config.read(config_file_path)

app_id = config['facebook']['app_id']
app_secret = config['facebook']['app_secret']
user_access_token = config['facebook']['user_access_token']

pp = pprint.PrettyPrinter(indent=2)

session = requests.session()

try:
    # args = {'access_token': user_access_token}
    #
    # response = session.request(method='GET',
    #                            url='https://graph.facebook.com/search?q=Tai Hwa Pork Noodle&type=place',
    #                            timeout=3000,
    #                            params=args)
    #
    # pp.pprint(response.headers)
    # pp.pprint(response.json())
    #
    # args = {'access_token': user_access_token,
    #         'fields': 'id,checkins,location'}
    #
    # response = session.request(method='GET',
    #                            url='https://graph.facebook.com/v2.8/153880607988046/',
    #                            timeout=3000,
    #                            params=args)
    #
    # pp.pprint(response.headers)
    # pp.pprint(response.json())
    #
    args = {'access_token': user_access_token}

    # albums
    # tagged

    response = session.request(method='GET',
                               url='https://graph.facebook.com/v2.8/1644972775731429/tagged/',
                               timeout=3000,
                               params=args)

    pp.pprint(response.headers)
    pp.pprint(response.json())

except requests.HTTPError as e:
    response = json.loads(e.read())
    pp.pprint(response)