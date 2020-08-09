import sys
import requests
from content_api.util import invalid_response
from content_api.model_api import make_model_api_with_validation
from content_api.model_routes import get_model_routes
from content_api.db import db

name = 'urls'

json_schema = {
  'type': 'object',
  'properties': {
      'id': db.id_json_schema,
      'url': {'type': 'string', 'format': 'uri', 'pattern': '^https?://.+$'},
      'created_at': {'type': 'string', 'format': 'date-time', 'x-meta': {'writable': False}},
      'updated_at': {'type': 'string', 'format': 'date-time', 'x-meta': {'writable': False}}
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
  data = request.get('body')
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
