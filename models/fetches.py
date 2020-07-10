name = 'fetches'

json_schema = {
  'type': 'object',
  'properties': {
  }
}

db_schema = f'''
  CREATE TABLE {name} (
    id serial PRIMARY KEY,
    url_id integer not null references urls(id),
    data text NOT NULL,
    created_at TIMESTAMP NOT NULL
  )
'''

db_migrations = []
