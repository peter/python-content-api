import sys
import os
import importlib
import db
from model_api import make_model_api
from model_routes import get_model_routes, default_route_names

ORDERED_MODEL_NAMES = [
  'urls',
  'fetches'
]

def set_model_defaults(name, model):
  if not 'name' in dir(model):
    setattr(model, 'name', name)
  if 'routes' in dir(model):
    setattr(model, 'routes', [{**r, 'model_name': name} for r in model.routes])
  else:
    if not ('db_schema' in dir(model) and 'json_schema' in dir(model)):
      raise Exception(f'You need to specify db_schema and json_schema for model {name}')
    setattr(model, 'api', make_model_api(name, model.json_schema))
    route_names = model.route_names if 'route_names' in dir(model) else default_route_names
    setattr(model, 'routes', get_model_routes(name, model.json_schema, model.api, route_names=route_names))
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
