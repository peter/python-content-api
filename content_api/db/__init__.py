import os
import importlib

DATABASE = os.environ.get('DATABASE', 'pg')
print(f'DATABASE={DATABASE}')
db = importlib.import_module(f'content_api.db.{DATABASE}')
