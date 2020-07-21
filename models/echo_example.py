def echo(request):
  return {'body': {'request': request}}

routes = [
  {
    'path': '/v1/echo',
    'handler': echo
  }
]
