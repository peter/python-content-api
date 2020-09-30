import sys
import os
import re
import traceback
import importlib
from content_api.db import db
from content_api.model_api import make_model_api
from content_api.model_routes import get_model_routes, default_route_names
from content_api.request_validation import decorate_handler_with_validation

def set_route_defaults(route, name):
  return {
    **route,
    'method': route.get('method', 'GET'),
    'name': route.get('name', route['handler'].__name__),
    'model_name': name,
    'handler': decorate_handler_with_validation(route)
  }

def set_model_defaults(default_name, model):
  if not 'name' in dir(model):
    setattr(model, 'name', default_name)
  if 'routes' not in dir(model):
    if not ('db_schema' in dir(model) and 'json_schema' in dir(model)):
      raise Exception(f'You need to specify db_schema and json_schema for model {name}')
    setattr(model, 'api', make_model_api(model.name, model.json_schema))
    route_names = model.route_names if 'route_names' in dir(model) else default_route_names
    setattr(model, 'routes', get_model_routes(model.name, model.json_schema, model.api, route_names=route_names))
  setattr(model, 'routes', [set_route_defaults(route, model.name) for route in model.routes])
  return model

def module_name(filename):
  name, ext = os.path.splitext(filename)
  if ext != '.py':
    return None
  return name

def default_model_name(module_name):
  (_, name_without_prefix) = re.match("^([0-9_-]+)?(.+)$", module_name).groups()
  return name_without_prefix

def all_models():
  module_names = sorted([module_name(f) for f in os.listdir('models') if module_name(f)])
  models = []
  for name in module_names:
    model = set_model_defaults(default_model_name(name), importlib.import_module(f'models.{name}'))
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
      print(f'Could not create schema for model {model.name}', error)
      traceback.print_exc()

def migrate_schema():
  # TODO: create db_migrations table if not exists
  # TODO: For each model, run any migrations not run (wrapped in a try/catch)
  pass

def all_model_routes():
  routes = []
  for model in all_models():
      routes += model.routes
  return routes
