import re
import json
import tornado
from tornado.web import Application, RequestHandler
from tornado.ioloop import IOLoop
from models import all_model_routes

def request_data(method, request):
  if not method in ['PUT', 'POST']:
    return None
  try:
    return json.loads(request.body)
  except:
    return None

class Handler(RequestHandler):
  def initialize(self, routes):
    self.routes = routes
  def handle_request(self, method, *params, **kwparams):
    route = self.routes.get(method)
    if not route:
      raise tornado.web.HTTPError(status_code=404, reason="Invalid method")
    query = {k: self.get_argument(k) for k in self.request.query_arguments}
    self.write({
      'method': route['method'],
      'route.path': route['path'],
      'path_params': kwparams,
      'data': request_data(route['method'], self.request),
      'headers': dict(self.request.headers),
      'query': query
    })
  def get(self, *params, **kwparams):
    self.handle_request('GET', *params, **kwparams)
  def put(self, *params, **kwparams):
    self.handle_request('PUT', *params, **kwparams)
  def post(self, *params, **kwparams):
    self.handle_request('POST', *params, **kwparams)
  def delete(self, *params, **kwparams):
    self.handle_request('DELETE', *params, **kwparams)

# Covert /v1/foobar/<id> to /v1/foobar/([^/]+)
def tornado_path(route_path):
  return re.sub(r'<([a-zA-Z0-9_]+)>', '(?P<\\1>[^/]+)', route_path)

def routes_by_path(routes):
  result = {}
  for route in routes:
    if not route['path'] in result:
      result[route['path']] = {}
    result[route['path']][route['method']] = route
  return result

def make_app():
  urls = []
  for path, routes in routes_by_path(all_model_routes()).items():
    urls.append((tornado_path(path), Handler, {'routes': routes}))
  return Application(urls)

if __name__ == '__main__':
    app = make_app()
    app.listen(5000)
    IOLoop.instance().start()
