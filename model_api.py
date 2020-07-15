import db
import re
from datetime import datetime
from json_schema import validate_schema, schema_error_response
from types import SimpleNamespace
from util import exception_response, invalid_response
from psycopg2.errors import UniqueViolation, ForeignKeyViolation
from json_schema import writable_schema, writable_doc

def is_valid_id(id):
  return re.match('\A[1-9][0-9]*\Z', id)

invalid_id_response = invalid_response('Invalid id - must be integer')

def remove_none(doc):
  return {k: v for k, v in doc.items() if v is not None}

def empty_decorator(operation):
  return operation

def make_model_api(table_name, json_schema,
  list_decorator=empty_decorator,
  get_decorator=empty_decorator,
  create_decorator=empty_decorator,
  update_decorator=empty_decorator,
  delete_decorator=empty_decorator):

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

  @list_decorator
  def list():
      docs = [remove_none(doc) for doc in db.query(f'select * from {table_name}')]
      return {'body': {'data': docs}}

  @get_decorator
  def get(id):
      if not is_valid_id(id):
        return invalid_id_response
      doc = db.query_one(f'select * from {table_name} where id = %s', [id])
      if not doc:
          return {'status': 404}
      return {'body': remove_none(doc)}

  @create_decorator
  def create(data):
      schema_error = validate_schema(data, write_schema)
      if schema_error:
        return schema_error_response(schema_error)
      doc = {**data, 'created_at': datetime.now()}
      try:
        id = db.insert(table_name, doc)
        created_doc = db.query_one(f'select * from {table_name} where id = %s', [id])
        return {'body': remove_none(created_doc)}
      except (UniqueViolation, ForeignKeyViolation) as db_error:
          return exception_response(db_error)

  @update_decorator
  def update(id, data):
      if not is_valid_id(id):
        return invalid_id_response
      data = writable_doc(json_schema, data)
      schema_error = validate_schema(data, write_schema)
      if schema_error:
        return schema_error_response(schema_error)
      try:
        doc = {**data, 'updated_at': datetime.now()}
        db.update(table_name, id, doc)
      except (UniqueViolation, ForeignKeyViolation) as db_error:
          return exception_response(db_error)
      updated_doc = db.query_one(f'select * from {table_name} where id = %s', [id])
      if not updated_doc:
          return {'status': 404}
      return {'body': remove_none(updated_doc)}

  @delete_decorator
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
