import os

import sqlite3

con = sqlite3.connect("db.sqlite", check_same_thread=False)
os.close(0)
con.close()
