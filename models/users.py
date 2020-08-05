from db import db

json_schema = {
  'type': 'object',
  'properties': {
    'id': db.id_json_schema,
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
