# Data Description

## Main Tables

Jiakbot main tables. Contain businesses, their categories and reviews and most importantly the statement and response pairs. 

* **businesses**
    * biz_id - TEXT
    * biz_name - TEXT
    * biz_categories - TEXT
    * biz_rating - NUMERIC
    * lat - NUMERIC
    * lng - NUMERIC
* **categories** - Main categories tables
    * biz_id - TEXT
    * biz_categories - TEXT
* **cuisines** - Extracted from categories (eg. japanese, chinese, indian etc)
    * biz_id - TEXT
    * cuisine - TEXT
* **food_types** - Extracted from categories (eg. noodles, rice etc)
    * biz_id - TEXT
    * food_type - TEXT
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