import os
import importlib

DATABASE = os.environ.get('DATABASE', 'pg')
db = importlib.import_module(f'content_api.db.{DATABASE}')
