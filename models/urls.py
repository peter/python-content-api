name = 'urls'

json_schema = {
  'type': 'object',
  'properties': {
      'id': {'type': 'integer', 'minimum': 1, 'x-meta': {'writable': False}},
      'url': {'type': 'string'},
      'created_at': {'type': 'string', 'x-meta': {'writable': False}},
      'updated_at': {'type': 'string', 'x-meta': {'writable': False}}
  },
  'required': ['id', 'url', 'created_at'],
  'additionalProperties': False
}

db_schema = f'''
  CREATE TABLE {name} (
    id serial PRIMARY KEY,
    url VARCHAR (355) UNIQUE NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP
  )
'''

db_migrations = []
