import sqlite3
conn = sqlite3.connect('backend/ppa.db')
with open('schema.txt', 'w') as f:
    for row in conn.execute("SELECT sql FROM sqlite_master WHERE type='table'"):
        if row[0]:
            f.write(row[0] + '\n\n')
