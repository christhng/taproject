from nltk.tokenize import sent_tokenize
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

# iterate through each record and create biz_id - category as a record
for result in results:

    review_id = result[0]
    description = result[1]

    # tokenize the sentence
    sent_tokens = sent_tokenize(description)
    print(sent_tokens)

    for sent_token in sent_tokens:
        record = [review_id,sent_token]
        records.append(record)

# insert into stg_categories table
c.executemany('INSERT INTO stmts (review_id,stmt) VALUES (?,?)', records)

conn.commit()
conn.close()
