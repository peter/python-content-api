json_schema = {
  'type': 'object',
  'properties': {
    'id': {'type': 'integer', 'minimum': 1, 'x-meta': {'writable': False}},
    'url_id': {'type': 'integer'},
    'data': {'type': 'string'},
    'created_at': {'type': 'string', 'x-meta': {'writable': False}}
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
