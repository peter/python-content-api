json_schema = {
  'type': 'object',
  'properties': {
    'id': {'type': 'integer', 'minimum': 1, 'x-meta': {'writable': False}},
    'email': {'type': 'string'}
  },
  'additionalProperties': False,
  'required': ['id', 'email']
}

db_schema = f'''
  CREATE TABLE users (
    id serial PRIMARY KEY,
    email text UNIQUE NOT NULL
  )
'''

route_names = ['list', 'get', 'create']
