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

@timer
@cache_header
def decorators_example(request):
  return {'body': {}}

routes = [
  {
    'path': '/v1/decorators_example',
    'handler': decorators_example
  },
]
