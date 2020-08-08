from content_api.util import with_decorators
from functools import wraps
import time

def with_headers(response, headers):
  return {**response, 'headers': {**response.get('headers', {}), **headers}}

def timer(handler):
  @wraps(handler)
  def with_timer(request):
    start_time = time.time()
    response = handler(request)
    elapsed = round((time.time() - start_time)*1000, 3)
    return with_headers(response, {'X-Response-Time': f'{elapsed}ms'})
  return with_timer

def cache_header(handler):
  @wraps(handler)
  def with_cache_header(request):
    response = handler(request)
    return with_headers(response, {'Cache-Control': 'max-age=120'})
  return with_cache_header

decorators = [
  timer,
  cache_header
]

@with_decorators(decorators)
def composed_decorators_example1(request):
  return {'body': {}}

@with_decorators(decorators)
def composed_decorators_example2(request):
  return {'body': {}}

routes = [
  {
    'path': '/v1/composed_decorators_example1',
    'handler': composed_decorators_example1
  },
  {
    'path': '/v1/composed_decorators_example2',
    'handler': composed_decorators_example2
  }
]
