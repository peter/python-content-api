import psycopg2
import psycopg2.extras
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
        created_at TIMESTAMP NOT NULL,
        updated_at TIMESTAMP
      )
    ''',
    '''
      CREATE TABLE fetches (
        id serial PRIMARY KEY,
        url_id integer not null references urls(id),
        data text NOT NULL,
        created_at TIMESTAMP NOT NULL
      )
    '''
  ]
  for table in tables:
    conn.cursor().execute(table)

def execute(*args):
    cur = conn.cursor()
    return cur.execute(*args)

def query_tuple(*args):
    cur = conn.cursor()
    cur.execute(*args)
    return cur.fetchall()

def query(*args):
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(*args)
    return list(map(dict, cur.fetchall()))

def query_one(conn, *args):
    rows = query(conn, *args)
    return rows[0] if len(rows) > 0 else None
