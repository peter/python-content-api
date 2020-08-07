import psycopg2
import psycopg2.extras
import os
import re

DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://postgres:@localhost/python-rest-api')
conn = psycopg2.connect(DATABASE_URL)
conn.autocommit = True

def execute(*args):
    cur = conn.cursor()
    cur.execute(*args)
    return cur

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

def where_sql(filter):
  if not filter:
    return ('', ())
  columns = filter.keys()
  def clause(column):
    if filter[column]['op'] == 'contains':
      return f'{column} like %s'
    else:
      return f'{column} = %s'
  def sql_value(column):
    value = filter[column]['value']
    if filter[column]['op'] == 'contains':
      return f'%{value}%'
    else:
      return value
  clauses = [clause(column) for column in columns]
  sql = 'WHERE ' + ' and '.join(clauses)
  values = tuple([sql_value(column) for column in columns])
  return (sql, values)

def order_sql(sort):
  if not sort:
    return ''
  def parse_order(item):
    direction = 'DESC' if item.startswith('-') else 'ASC'
    name = item[1:] if item.startswith('-') else item
    return {'direction': direction, 'name': name}
  columns = [parse_order(item) for item in sort.split(',')]
  assert_valid_columns([c['name'] for c in columns])
  return 'ORDER BY ' + ', '.join([f'{c["name"]} {c["direction"]}' for c in columns])

#############################################################
#
# Database Interface
#
#############################################################

id_json_schema = {'type': 'integer', 'minimum': 1, 'x-meta': {'writable': False}}

def count(table_name):
  return query_one(f'select count(*) from {table_name}')['count']

def find(table_name, limit=100, offset=0, sort=None, filter=None):
  (where_clauses, where_values) = where_sql(filter)
  values = where_values + (limit, offset)
  sql = f'select * from {table_name} {where_clauses} {order_sql(sort)} LIMIT %s OFFSET %s'
  print(f'find sql={sql} values={values}')
  return query(sql, values)

def find_one(table_name, id):
  return query_one(f'select * from {table_name} where id = %s', [id])

def create(table_name, doc):
  columns = list(doc.keys())
  assert_valid_columns(columns)
  values = [doc[k] for k in columns]
  interpolate_values = ['%s' for _ in values]
  sql = f'INSERT INTO {table_name} ({", ".join(columns)}) VALUES ({", ".join(interpolate_values)}) RETURNING id'
  print(sql)
  cur = execute(sql, values)
  id = cur.fetchone()[0]
  return id

def update(table_name, id, doc):
  columns = list(doc.keys())
  assert_valid_columns(columns)
  interpolate_values = [f'{c} = %s' for c in columns]
  values = [doc[k] for k in columns] + [id]
  sql = f'UPDATE {table_name} SET {", ".join(interpolate_values)} where id = %s'
  print(sql)
  return execute(sql, values)

def delete(table_name, id):
  return execute(f'DELETE from {table_name} where id = %s', [id])
