import os
import importlib

framework = os.environ.get('FRAMEWORK', 'flask')
app = importlib.import_module(f'{framework}_app').app
