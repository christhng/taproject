# script to prepare cuisine (c), food (f), place (p)
# TODO - import from mappings

import sqlite3

db_path = '../../database/jiakbot.db'

# connect and write to database
conn = sqlite3.connect(db_path)
c = conn.cursor()

del_c_sql = "delete from cuisines;"
del_f_sql = "delete from foods;"
del_p_sql = "delete from places;"

c.execute(del_c_sql)
c.execute(del_f_sql)
c.execute(del_p_sql)

conn.commit()

c_sql = "INSERT INTO cuisines (biz_id, cuisine) " + \
        "SELECT sc.biz_id, sc.biz_category FROM stg_categories sc " + \
        "LEFT JOIN stg_mappings sm ON sc.biz_category=sm.biz_category " + \
        "WHERE sm.mapped_item='cuisine'; "


f_sql = "INSERT INTO foods (biz_id, food) " + \
        "SELECT sc.biz_id, sc.biz_category FROM stg_categories sc " + \
        "LEFT JOIN stg_mappings sm ON " + \
        "sc.biz_category=sm.biz_category " + \
        "WHERE sm.mapped_item='food';"

p_sql = "INSERT INTO places (biz_id, place) " + \
        "SELECT sc.biz_id, sc.biz_category FROM stg_categories sc " + \
        "LEFT JOIN stg_mappings sm ON sc.biz_category=sm.biz_category " + \
        "WHERE sm.mapped_item='place'; "

c.execute(c_sql)
c.execute(f_sql)
c.execute(p_sql)

conn.commit()
conn.close()