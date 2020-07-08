import psycopg2
import urllib.parse as urlparse
import os

DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://postgres:@localhost/python-heroku-kitchensink')
conn = psycopg2.connect(DATABASE_URL)
conn.autocommit = True

def create_schema():
  tables = [
    '''
      CREATE TABLE urls (
        id serial PRIMARY KEY,
        url VARCHAR (355) UNIQUE NOT NULL,
        createdAt TIMESTAMP NOT NULL,
        updatedAt TIMESTAMP
      )
    ''',
    '''
      CREATE TABLE fetches (
        id serial PRIMARY KEY,
        url_id integer not null references urls(id),
        data text NOT NULL,
        createdAt TIMESTAMP NOT NULL
      )
    '''
  ]
  for table in tables:
    conn.cursor().execute(table)
