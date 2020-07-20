import time

def with_headers(response, headers):
  return {**response, 'headers': {**response.get('headers', {}), **headers}}

def timer(handler):
  def with_timer(**kwargs):
    start_time = time.time()
    response = handler(**kwargs)
    elapsed = round((time.time() - start_time)*1000, 3)
    print(f'timer elapsed={elapsed}')
    return with_headers(response, {'X-Response-Time': f'{elapsed}ms'})
  return with_timer

def cache_header(handler):
  def with_cache_header(**kwargs):
    response = handler(**kwargs)
    return with_headers(response, {'Cache-Control': 'max-age=120'})
  return with_cache_header

@timer
@cache_header
def hello(**kwargs):
  return {'body': {'hello': 'World!'}}

routes = [
  {
    'path': '/v1/hello',
    'handler': hello
  }
]
