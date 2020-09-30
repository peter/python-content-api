import re
from datetime import datetime
from content_api.json_schema import validate_schema, schema_error_response, coerce_value, writable_doc
from types import SimpleNamespace
from content_api.db import db
import content_api.util as util
from content_api.util import exception_response, invalid_response, remove_none
from psycopg2.errors import UniqueViolation, ForeignKeyViolation

def empty_decorator(operation):
  return operation

def is_valid_sort(json_schema, sort):
  if not sort:
    return True
  for item in sort.split(','):
    name = item[1:] if item.startswith('-') else item
    if not name in json_schema['properties'].keys():
      return False
  return True

def filter_param_pattern(json_schema):
  property_names = json_schema['properties'].keys()
  return f'^filter\\.({"|".join(property_names)})(?:\\[(contains|lt|gt)\\])?$'

def parse_filter(json_schema, query):
  pattern = re.compile(filter_param_pattern(json_schema))
  result = {}
  for k, v in query.items():
    match = re.match(pattern, k)
    if match:
      (name, op) = match.groups()
      value_schema = util.get(json_schema, f'properties.{name}')
      result[name] = {
        'value': coerce_value(v, value_schema),
        'op': (op or 'eq')
      }
  return result

def make_model_api(table_name, json_schema,
  list_decorator=empty_decorator,
  get_decorator=empty_decorator,
  create_decorator=empty_decorator,
  update_decorator=empty_decorator,
  delete_decorator=empty_decorator):

  def response_schema(operation):
    if operation == 'list':
      return {
        'type': 'object',
        'properties': {
          'data': {
            'type': 'array',
            'items': json_schema
          },
          'count': {'type': 'integer'},
          'limit': {'type': 'integer'},
          'offset': {'type': 'integer'},
          'sort': {'type': 'string'},
          'filter': {'type': 'object'}
        },
        'additionalProperties': False,
        'required': ['data', 'count', 'limit', 'offset']
      }
    else:
      return json_schema

  @list_decorator
  def list(request):
      limit = int(util.get(request, 'query.limit', 100))
      offset = int(util.get(request, 'query.offset', 0))
      sort = util.get(request, 'query.sort') or '-updated_at'
      if not is_valid_sort(json_schema, sort):
        return invalid_response('Invalid sort parameter, must be on the format column1,column2,column3... For descending sort, use -column1')
      filter = parse_filter(json_schema, request.get('query', {}))
      count = db.count(table_name, filter)
      docs = [remove_none(doc) for doc in db.find(table_name, limit, offset, sort, filter)]
      body = {
        'count': count,
        'limit': limit,
        'offset': offset,
        'sort': sort,
        'filter': filter,
        'data': docs
      }
      return {'body': body}

  @get_decorator
  def get(request):
      id = request.get('path_params')['id']
      doc = db.find_one(table_name, id)
      if not doc:
          return {'status': 404}
      return {'body': remove_none(doc)}

  @create_decorator
  def create(request):
      data = writable_doc(json_schema, request.get('body'))
      if 'created_at' in json_schema['properties'] and 'updated_at' in json_schema['properties']:
        now = datetime.now()
        data = {**data, 'created_at': now, 'updated_at': now}
      try:
        id = db.create(table_name, data)
        created_doc = db.find_one(table_name, id)
        return {'body': remove_none(created_doc)}
      except (UniqueViolation, ForeignKeyViolation) as db_error:
          return exception_response(db_error)

  @update_decorator
  def update(request):
      id = request.get('path_params')['id']
      data = writable_doc(json_schema, request.get('body'))
      try:
        if 'updated_at' in json_schema['properties']:
          data = {**data, 'updated_at': datetime.now()}
        db.update(table_name, id, data)
      except (UniqueViolation, ForeignKeyViolation) as db_error:
          return exception_response(db_error)
      updated_doc = db.find_one(table_name, id)
      if not updated_doc:
          return {'status': 404}
      return {'body': remove_none(updated_doc)}

  @delete_decorator
  def delete(request):
      id = request.get('path_params')['id']
      doc = db.find_one(table_name, id)
      if not doc:
          return {'status': 404}
      db.delete(table_name, id)
      return {'body': remove_none(doc)}

  api = {
    'response_schema': response_schema,
    'list': list,
    'get': get,
    'create': create,
    'update': update,
    'delete': delete
  }
  return SimpleNamespace(**api)

def empty_validate(request):
  return None

def make_model_api_with_validation(name, json_schema, validate=empty_validate):
  def create_with_validation(_create):
    def create(request):
      invalid_message = validate(request)
      if invalid_message:
        return invalid_response(invalid_message)
      return _create(request)
    return create

  def update_with_validation(_update):
    def update(request):
      invalid_message = validate(request)
      if invalid_message:
        return invalid_response(invalid_message)
      return _update(request)
    return update

  return make_model_api(name, json_schema,
    create_decorator=create_with_validation,
    update_decorator=update_with_validation)
