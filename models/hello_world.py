import time

def timer(handler):
  def with_timer(**kwargs):
    start_time = time.time()
    result = handler(**kwargs)
    elapsed = time.time() - start_time
    print(f'timer elapsed={elapsed}')
    return result
  return with_timer

def cache_header(handler):
  def with_cache_header(**kwargs):
    result = handler(**kwargs)
    return {
      **result,
      'headers': {**result.get('headers', {}), 'Cache-Control': 'max-age=120'}
    }
  return with_cache_header

@timer
@cache_header
def hello(**kwargs):
  return {'body': 'Hello World!'}

routes = [
  {
    'path': '/v1/hello',
    'handler': hello
  }
]
