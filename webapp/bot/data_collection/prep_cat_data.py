
import sqlite3
db_path = '../../database/jiakbot.db'
# connect and write to database
conn = sqlite3.connect(db_path)
c = conn.cursor()

# get all biz ids
c.execute('SELECT biz_id, biz_categories FROM businesses')
results = c.fetchall()

records = []

# clear the table
del_cat_sql = "delete from stg_categories;"
c.execute(del_cat_sql)

conn.commit()

# iterate through each record and create biz_id - category as a record
for result in results:
    biz_id = result[0]
    cats = result[1]
    cat_list = cats.split('|')

    for cat in cat_list:
        record = [biz_id,cat]
        records.append(record)

# insert into stg_categories table
c.executemany('INSERT INTO stg_categories VALUES (?,?)', records)

conn.commit()
conn.close()
