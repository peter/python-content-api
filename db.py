import psycopg2
import psycopg2.extras
import os
import re

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

def query_one(*args):
    rows = query(*args)
    return rows[0] if len(rows) > 0 else None

def is_valid_column(column):
  return re.match('\A[a-zA-Z0-9_]+\Z', column)

def assert_valid_columns(columns):
  # sanity check columns to protect against SQL injection
  invalid_columns = [c for c in columns if not is_valid_column(c)]
  if invalid_columns:
    raise Exception(f'Invalid column names: {invalid_columns}')

def insert(table_name, doc):
  columns = list(doc.keys())
  assert_valid_columns(columns)
  values = [doc[k] for k in columns]
  interpolate_values = ['%s' for _ in values]
  sql = f'INSERT INTO {table_name} ({", ".join(columns)}) VALUES ({", ".join(interpolate_values)}) RETURNING id'
  return execute(sql, values)

def update(table_name, id, doc):
  columns = list(doc.keys())
  assert_valid_columns(columns)
  interpolate_values = [f'SET {c} = %s' for c in columns]
  values = [doc[k] for k in columns] + [id]
  sql = f'UPDATE {table_name} {" ".join(interpolate_values)} where id = %s'
  execute(sql, values)
