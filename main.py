import uvicorn
import psycopg2
import redis
from elasticsearch import Elasticsearch

if __name__ == "__main__":
    uvicorn.run("app.api:app", host="127.0.0.1", port=8081, reload=True)

con = psycopg2.connect(database="library", user="postgres", password="admin", host="127.0.0.1", port="5432")
cur = con.cursor()
try:
    cur.execute('''CREATE TABLE users(
        id BIGSERIAL NOT NULL PRIMARY KEY,
        email VARCHAR(100) NOT NULL UNIQUE,
        password VARCHAR(100) NOT NULL,
        role VARCHAR(10) NOT NULL);
        CREATE TABLE book(
        id BIGSERIAL NOT NULL PRIMARY KEY,
        title VARCHAR(100) NOT NULL UNIQUE,
        borrowed_by BIGINT REFERENCES users (id) DEFAULT NULL,
        date_borrowed DATE DEFAULT NULL,
        author VARCHAR(100),
        des TEXT);''')
except psycopg2.errors.DuplicateTable:
    pass
con.commit()
# con.close()

r = redis.Redis(host="127.0.0.1", port="6379")
es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
