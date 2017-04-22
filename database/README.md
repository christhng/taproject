# Data Description

The data is for demonstration purposes only.

## Main Tables

Jiakbot main tables. Contain businesses, their categories and reviews and most importantly the statement and response pairs.

* **businesses**
    * biz_id - TEXT
    * biz_name - TEXT
    * biz_categories - TEXT
    * biz_rating - NUMERIC
    * lat - NUMERIC
    * lng - NUMERIC
* **cuisines** - Extracted from categories (eg. japanese, chinese, indian etc)
    * biz_id - TEXT
    * cuisine - TEXT
* **foods** - Extracted from categories (eg. noodles, rice etc)
    * biz_id - TEXT
    * food - TEXT
* **places** - Extracted from categories (eg. foodcourt, izakayas etc). Not in use at the moment
    * biz_id - TEXT
    * place - TEXT
* **reviews**
    * biz_id - TEXT
    * author - TEXT
    * published - TEXT
    * rating - NUMERIC
    * desc - TEXT

## Staging Tables

* Tables prefixed with stg_ .
* These tables essentially have the same structure as the main tables but used for data processing purposes.
* The data extracted from APIs and web scraping are stored here.
* Tables with only staging are ...

* **stg_categories** - Holds the normalized categories of businesses
    * biz_id - TEXT
    * biz_category - TEXT
* **stg_mappings** - Holds the mappings of categories to food ,places,cuisines.
    * biz_id - TEXT
    * mapped_item - TEXT
