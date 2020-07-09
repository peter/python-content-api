import db
from datetime import datetime
from json_schema import validate_schema, validate_response
from types import SimpleNamespace

def make_model_api(table_name, json_schema):
  def list():
      rows = db.query(f'select * from {table_name}')
      return {'body': rows}

  def get(id):
      row = db.query_one(f'select * from {table_name} where id = %s', [id])
      if not row:
          return {'status': 404}
      return {'body': row}

  def create(data):
      schema_error = validate_schema(data, json_schema)
      if schema_error:
        return validate_response(schema_error)
      doc = {**data, 'created_at': datetime.now()}
      id = db.insert(table_name, doc)
      created_doc = db.query_one(f'select * from {table_name} where id = %s', [id])
      return {'body': created_doc}

  def update(id, data):
      schema_error = validate_schema(data, json_schema)
      if schema_error:
        return validate_response(schema_error)
      db.update(table_name, id, data)
      updated_doc = db.query_one(f'select * from {table_name} where id = %s', [id])
      if not updated_doc:
          return {'status': 404}
      return {'body': updated_doc}

  def delete(id):
      row = db.query_one(f'select * from {table_name} where id = %s', [id])
      if not row:
          return {'status': 404}
      db.execute(f'DELETE from {table_name} where id = %s', [id])
      return {}

  return SimpleNamespace(**{
    'list': list,
    'get': get,
    'create': create,
    'update': update,
    'delete': delete
  })
