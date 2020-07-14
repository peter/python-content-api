import db
import re
from datetime import datetime
from json_schema import validate_schema, validate_response
from types import SimpleNamespace
from util import exception_body
from psycopg2.errors import UniqueViolation, ForeignKeyViolation
from json_schema import writable_schema, writable_doc

def db_validation_response(db_error):
    return {'body': exception_body(db_error), 'status': 400}

def is_valid_id(id):
  return re.match('\A[1-9][0-9]*\Z', id)

invalid_id_response = {'body': {'error': {'message': 'Invalid id - must be integer'}}, 'status': 400}

def remove_none(doc):
  return {k: v for k, v in doc.items() if v is not None}

def make_model_api(table_name, json_schema):
  write_schema = writable_schema(json_schema)

  def response_schema(operation):
    if operation == 'list':
      return {
        'type': 'object',
        'properties': {
          'data': {
            'type': 'array',
            'items': json_schema
          }
        },
        'additionalProperties': False,
        'required': ['data']
      }
    else:
      return json_schema

  def list():
      docs = [remove_none(doc) for doc in db.query(f'select * from {table_name}')]
      return {'body': {'data': docs}}

  def get(id):
      if not is_valid_id(id):
        return invalid_id_response
      doc = db.query_one(f'select * from {table_name} where id = %s', [id])
      if not doc:
          return {'status': 404}
      return {'body': remove_none(doc)}

  def create(data):
      schema_error = validate_schema(data, write_schema)
      if schema_error:
        return validate_response(schema_error)
      doc = {**data, 'created_at': datetime.now()}
      try:
        id = db.insert(table_name, doc)
        created_doc = db.query_one(f'select * from {table_name} where id = %s', [id])
        return {'body': remove_none(created_doc)}
      except (UniqueViolation, ForeignKeyViolation) as db_error:
          return db_validation_response(db_error)

  def update(id, data):
      if not is_valid_id(id):
        return invalid_id_response
      data = writable_doc(json_schema, data)
      schema_error = validate_schema(data, write_schema)
      if schema_error:
        return validate_response(schema_error)
      try:
        doc = {**data, 'updated_at': datetime.now()}
        db.update(table_name, id, doc)
      except (UniqueViolation, ForeignKeyViolation) as db_error:
          return db_validation_response(db_error)
      updated_doc = db.query_one(f'select * from {table_name} where id = %s', [id])
      if not updated_doc:
          return {'status': 404}
      return {'body': remove_none(updated_doc)}

  def delete(id):
      if not is_valid_id(id):
        return invalid_id_response
      doc = db.query_one(f'select * from {table_name} where id = %s', [id])
      if not doc:
          return {'status': 404}
      db.execute(f'DELETE from {table_name} where id = %s', [id])
      return {'body': remove_none(doc)}

  return SimpleNamespace(**{
    'response_schema': response_schema,
    'list': list,
    'get': get,
    'create': create,
    'update': update,
    'delete': delete
  })
