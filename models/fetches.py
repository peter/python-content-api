json_schema = {
  'type': 'object',
  'properties': {
  }
}

db_schema = '''
  CREATE TABLE fetches (
    id serial PRIMARY KEY,
    url_id integer not null references urls(id),
    data text NOT NULL,
    created_at TIMESTAMP NOT NULL
  )
'''

db_migrations = []
