import sys
import requests
from util import invalid_response
from model_api import make_model_api_with_validation
from model_routes import get_model_routes

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

def validate_url(request):
  data = request.get('data')
  if not data or not 'url' in data:
    return None
  try:
    result = requests.get(data['url'], timeout=5)
    if result.status_code != 200:
      return f'Expected status code 200 for for url {data["url"]} but got {result.status_code}'
  except:
    error = sys.exc_info()[0]
    return f'Could not fetch url {data["url"]}: {error}'

api = make_model_api_with_validation(name, json_schema, validate=validate_url)

routes = get_model_routes(name, json_schema, api)
