from content_api.db import db

json_schema = {
  'type': 'object',
  'properties': {
    'id': db.id_json_schema,
    'url_id': {'type': 'integer'},
    'data': {'type': 'string'},
    'created_at': {'type': 'string', 'format': 'date-time', 'x-meta': {'writable': False}},
    'updated_at': {'type': 'string', 'format': 'date-time', 'x-meta': {'writable': False}}
  },
  'additionalProperties': False,
  'required': ['id', 'url_id', 'data', 'created_at']
}

db_schema = f'''
  CREATE TABLE fetches (
    id serial PRIMARY KEY,
    url_id integer not null references urls(id),
    data text NOT NULL,
    created_at TIMESTAMP NOT NULL
  )
'''
