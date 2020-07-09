import db
from datetime import datetime
from json_schema import validate_schema, validate_response

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

def list():
    rows = db.query('select * from urls')
    return {'body': rows}

def get(url_id):
    row = db.query_one("select * from urls where id = %s", [url_id])
    if not row:
        return {'status': 404}
    return {'body': row}

def create(data):
    schema_error = validate_schema(data, json_schema)
    if schema_error:
      return validate_response(schema_error)
    doc = {**data, 'created_at': datetime.now()}
    url_id = db.insert('urls', doc)
    created_doc = db.query_one("select * from urls where id = %s", [url_id])
    return {'body': created_doc}

def update(url_id, data):
    schema_error = validate_schema(data, json_schema)
    if schema_error:
      return validate_response(schema_error)
    db.update('urls', url_id, data)
    updated_doc = db.query_one("select * from urls where id = %s", [url_id])
    if not updated_doc:
        return {'status': 404}
    return {'body': updated_doc}

def delete(url_id):
    row = db.query_one("select * from urls where id = %s", [url_id])
    if not row:
        return {'status': 404}
    db.execute('DELETE from urls where id = %s', [url_id])
    return {}
