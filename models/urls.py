import sys
import requests
from util import invalid_response
from model_api import make_model_api

name = 'urls'

json_schema = {
  'type': 'object',
  'properties': {
      'id': {'type': 'integer', 'minimum': 1, 'x-meta': {'writable': False}},
      'url': {'type': 'string', 'format': 'uri', 'pattern': '^https?://.+$'},
      'created_at': {'type': 'string', 'x-meta': {'writable': False}},
      'updated_at': {'type': 'string', 'x-meta': {'writable': False}}
  },
  'required': ['id', 'url', 'created_at'],
  'additionalProperties': False
}

db_schema = f'''
  CREATE TABLE {name} (
    id serial PRIMARY KEY,
    url VARCHAR (355) UNIQUE NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP
  )
'''

db_migrations = []

def validate_url(data):
  if not data or not 'url' in data:
    return None
  try:
    result = requests.get(data['url'])
    if result.status_code != 200:
      return f'Expected status code 200 for for url {data["url"]} but got {result.status_code}'
  except:
    error = sys.exc_info()[0]
    return f'Could not fetch url {data["url"]}: {error}'

def create_with_validation(_create):
  def create(data):
    invalid_message = validate_url(data)
    if invalid_message:
      return invalid_response(invalid_message)
    return _create(data)
  return create

def update_with_validation(_update):
  def update(id, data):
    invalid_message = validate_url(data)
    if invalid_message:
      return invalid_response(invalid_message)
    return _update(id, data)
  return update

api = make_model_api(name, json_schema,
  create_decorator=create_with_validation,
  update_decorator=update_with_validation)
