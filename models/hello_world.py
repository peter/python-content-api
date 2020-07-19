import time

def timer(handler):
  def with_timer(**kwargs):
    start_time = time.time()
    result = handler(**kwargs)
    elapsed = time.time() - start_time
    print(f'timer elapsed={elapsed}')
    return result
  return with_timer

@timer
def hello(**kwargs):
  return {'body': 'Hello World!'}

routes = [
  {
    'path': '/v1/hello',
    'handler': hello
  }
]
