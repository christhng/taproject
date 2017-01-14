**For authenticating with Yelp's API ...**

**Create an auth.ini file in /config_auth/ with the following content**

```python
[yelp]
consumer_key=asdf23dDf2_dFdfdfs
consumer_secret=AdGT54DFdfHtGh5345GFDehRggDdfHUU54SSDsssdf
access_token_key=asdf34dfaf9dDFadsDf
access_token_secret=asdfdfDf3feERefdffd
client_id=asldkfj2l3k4jlkj234
client_secret=k4jlkdlkfj3k4jkjdkj34kj
```

* Note: client_id/secret is for oauth2, while the rest is for oauth1

* The above is fake, for obvious reasons. The file will be read in by 00_get_data.py and used to authenticate against Yelp to extract data. The ini file will be ignored by git.
