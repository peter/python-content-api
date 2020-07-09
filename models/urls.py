json_schema = {
  'type': 'object',
  'properties': {
      'url': {'type': 'string'},
  },
  'required': ['url'],
  'additionalProperties': False
}

db_schema = '''
  CREATE TABLE urls (
    id serial PRIMARY KEY,
    url VARCHAR (355) UNIQUE NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP
  )
'''

db_migrations = []