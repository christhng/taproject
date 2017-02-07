import sqlite3

db_path = '../../database/jiakbot.db'

# connect and write to database
conn = sqlite3.connect(db_path)
c = conn.cursor()

'SELECT '