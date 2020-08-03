import re
import json
import os
from datetime import date
import tornado
from tornado.web import Application, RequestHandler
from tornado.ioloop import IOLoop
from models import all_model_routes

class JsonEncoder(json.JSONEncoder):
	def default(self, obj):
		if isinstance(obj, date): # ISO date formating
			return str(obj)
		return json.JSONEncoder.default(self, obj)

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
    self.set_header('Content-Type', 'application/json')
    route = self.routes.get(method)
    if not route:
      self.set_status(405)
      return self.finish()
    query = {k: self.get_argument(k) for k in self.request.query_arguments}
    response = route['handler']({
      'path_params': kwparams,
      'data': request_data(route['method'], self.request),
      'headers': dict(self.request.headers),
      'query': query})
    self.set_status(response.get('status', 200))
    body = json.dumps(response.get('body', {}), indent=4, cls=JsonEncoder)
    self.finish(body)
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
    port = int(os.environ.get('PORT', 5000))
    app.listen(port)
    IOLoop.instance().start()
