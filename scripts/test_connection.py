import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
)

cur = conn.cursor()
cur.execute("SELECT current_database(), current_user;")
result = cur.fetchone()

print("Connected to:", result[0])
print("User:", result[1])

cur.close()
conn.close()