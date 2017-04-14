from nltk.tokenize import sent_tokenize
from nltk.tokenize import word_tokenize
import nltk
import re

import sqlite3

db_path = '../../database/jiakbot.db'

# connect and write to database
conn = sqlite3.connect(db_path)
c = conn.cursor()

# get all biz ids
c.execute('SELECT review_id, description FROM reviews')
results = c.fetchall()
records = []

# clear the table
del_stmt_sql = "DELETE FROM stmts;"
c.execute(del_stmt_sql)

conn.commit()

# initialize the stop words removal and stemming
stop_list = nltk.corpus.stopwords.words('english')
stemmer = nltk.stem.porter.PorterStemmer()

# iterate through each record and create biz_id - category as a record
for result in results:

    review_id = result[0]
    description = result[1]

    # tokenize the sentence
    sent_tokens = sent_tokenize(description)


    for sent_token in sent_tokens:
        #print(sent_token)

        # tokenize the stmt
        cleansed = word_tokenize(sent_token)
        #print(cleansed)

        # convert to lower case
        cleansed = [w.lower() for w in cleansed]
        #print(cleansed)

        # remove punctuation
        cleansed = [w for w in cleansed if re.search('^[a-z]+$', w)]
        #print(cleansed)

        # remove stopwords
        # cleansed = [w for w in cleansed if w not in stop_list]
        #print(cleansed)

        # stem the statement
        #cleansed = [stemmer.stem(w) for w in cleansed]
        #print(cleansed)

        if len(cleansed) > 1:

            # join using pipe
            cleansed = "|".join([w for w in cleansed])
            #print(cleansed)

            record = [review_id,sent_token, cleansed]
            records.append(record)

# insert into stg_categories table
c.executemany('INSERT INTO stmts (review_id,stmt,stmt_cleansed) VALUES (?,?,?)', records)

conn.commit()
conn.close()
