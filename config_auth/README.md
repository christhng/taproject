For authenticating with Yelp's API ...

**Create an auth.ini file with the following content**

[yelp_app]
app_id=asdf23dDf2_dFdfdfs
app_secret=AdGT54DFdfHtGh5345GFDehRggDdfHUU54SSDsssdf

The above is fake, for obvious reasons.

The file will be read in by 00_get_data.py and used to authenticate against Yelp to extract data. 

The ini file will be ignored by git.
