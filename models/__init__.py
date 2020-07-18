import sys
import os
import importlib
import db
from model_api import make_model_api
from model_routes import get_model_routes, default_route_names
from json_schema import validate_schema, schema_error_response
from util import invalid_response

ORDERED_MODEL_NAMES = [
  'urls',
  'fetches'
]

def parameters_schema(parameters):
  properties = {p['name']: p['schema'] for p in parameters}
  required = [p['name'] for p in parameters if p.get('required') == True]
  return {
    'type': 'object',
    'properties': properties,
    'required': required,
    'additionalProperties': False
  }

def validate_parameters(route, query, **kwargs):
  if 'parameters' not in route:
    return None
  query_parameters = [p for p in route['parameters'] if p['in'] == 'query']
  if query_parameters and query:
    return validate_schema(query, parameters_schema(query_parameters))

def decorate_handler_with_validation(route):
  def handler_with_validation(**kwargs):
    schema_error = validate_parameters(route, **kwargs)
    if schema_error:
      return schema_error_response(schema_error)
    return route['handler'](**kwargs)
  handler_with_validation.__name__ = route['handler'].__name__
  return handler_with_validation

def set_route_defaults(route, name):
  return {
    **route,
    'model_name': name,
    'handler': decorate_handler_with_validation(route)
  }

def set_model_defaults(name, model):
  if not 'name' in dir(model):
    setattr(model, 'name', name)
  if 'routes' not in dir(model):
    if not ('db_schema' in dir(model) and 'json_schema' in dir(model)):
      raise Exception(f'You need to specify db_schema and json_schema for model {name}')
    setattr(model, 'api', make_model_api(name, model.json_schema))
    route_names = model.route_names if 'route_names' in dir(model) else default_route_names
    setattr(model, 'routes', get_model_routes(name, model.json_schema, model.api, route_names=route_names))
  setattr(model, 'routes', [set_route_defaults(route, name) for route in model.routes])
  return model

def all_models():
  def model_name(filename):
    name, ext = os.path.splitext(filename)
    if filename != os.path.basename(__file__) and ext == '.py':
      return name
  def is_unordered_model(filename):
    name = model_name(filename)
    return name and name not in ORDERED_MODEL_NAMES
  def get_unordered_names():
    return [model_name(f) for f in os.listdir('models') if is_unordered_model(f)]
  models = []
  for name in (ORDERED_MODEL_NAMES + get_unordered_names()):
    model = set_model_defaults(name, importlib.import_module(f'models.{name}'))
    models.append(model)
  return models

def create_schema():
  models = [model for model in all_models() if 'db_schema' in dir(model)]
  for model in models:
    try:
      print(f'model: {model.name}')
      print(model.db_schema)
      db.conn.cursor().execute(model.db_schema)
    except:
      error = sys.exc_info()[0]
      print(f'Could not create schema for model {model.name}: {error}')

def migrate_schema():
  # TODO: create db_migrations table if not exists
  # TODO: For each model, run any migrations not run (wrapped in a try/catch)
  pass

def all_model_routes():
  routes = []
  for model in all_models():
      routes += model.routes
  return routes
