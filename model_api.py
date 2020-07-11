import db
import re
from datetime import datetime
from json_schema import validate_schema, validate_response
from types import SimpleNamespace
from util import exception_body
from psycopg2.errors import UniqueViolation

def unique_response(unique_error):
    return {'body': exception_body(unique_error), 'status': 400}

def is_valid_id(id):
  return re.match('\A[1-9][0-9]*\Z', id)

invalid_id_response = {'body': {'error': {'message': 'Invalid id - must be integer'}}, 'status': 400}

def make_model_api(table_name, json_schema):
  def list():
      rows = db.query(f'select * from {table_name}')
      return {'body': rows}

  def get(id):
      if not is_valid_id(id):
        return invalid_id_response
      row = db.query_one(f'select * from {table_name} where id = %s', [id])
      if not row:
          return {'status': 404}
      return {'body': row}

  def create(data):
      schema_error = validate_schema(data, json_schema)
      if schema_error:
        return validate_response(schema_error)
      doc = {**data, 'created_at': datetime.now()}
      try:
        id = db.insert(table_name, doc)
        created_doc = db.query_one(f'select * from {table_name} where id = %s', [id])
        return {'body': created_doc}
      except UniqueViolation as unique_error:
          return unique_response(unique_error)

  def update(id, data):
      if not is_valid_id(id):
        return invalid_id_response
      schema_error = validate_schema(data, json_schema)
      if schema_error:
        return validate_response(schema_error)
      try:
        db.update(table_name, id, data)
      except UniqueViolation as unique_error:
          return unique_response(unique_error)
      updated_doc = db.query_one(f'select * from {table_name} where id = %s', [id])
      if not updated_doc:
          return {'status': 404}
      return {'body': updated_doc}

  def delete(id):
      if not is_valid_id(id):
        return invalid_id_response
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
