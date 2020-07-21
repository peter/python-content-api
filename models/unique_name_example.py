# NOTE: this example may not seem to make too much sense, but there is an
# issue with Flask where handler names need to be unique, i.e. you can't
# reuse the same handler in multiple routes. We have a workaround for this
# in flask_app.py and here I just wanted to check that reusing a handler works.

def hello(request):
  return {'body': {'hello': 'World!'}}

routes = [
  {
    'path': '/v1/hello1',
    'handler': hello
  },
  {
    'path': '/v1/hello2',
    'handler': hello
  }
]
