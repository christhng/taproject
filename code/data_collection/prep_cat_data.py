
import sqlite3
db_path = '../../database/jiakbot.db'
# connect and write to database
conn = sqlite3.connect(db_path)
c = conn.cursor()

# get all biz ids
c.execute('SELECT biz_id, biz_categories FROM businesses')
results = c.fetchall()

records = []

for result in results:
    biz_id = result[0]
    cats = result[1]
    cat_list = cats.split('|')

    for cat in cat_list:
        record = [biz_id,cat]
        records.append(record)

c.executemany('INSERT INTO stg_categories VALUES (?,?)', records)

conn.commit()
conn.close()
