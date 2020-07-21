def hello(request):
  return {'body': {'hello': 'World!'}}

routes = [
  {
    'path': '/v1/hello',
    'handler': hello
  }
]
