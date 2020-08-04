import re
import json
import os
from datetime import date
import tornado.ioloop
import tornado.web
from tornado.web import Application, RequestHandler
from tornado.log import enable_pretty_logging
from swagger import generate_swagger
from models import all_model_routes

class JsonEncoder(json.JSONEncoder):
	def default(self, obj):
		if isinstance(obj, date): # ISO date formating
			return str(obj)
		return json.JSONEncoder.default(self, obj)

def to_json(data):
  return json.dumps(data, indent=4, cls=JsonEncoder)

def request_body(method, request):
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
    self.set_header('Content-Type', 'application/json')
    if not route:
      self.set_status(405)
      self.finish()
      return
    query = {k: self.get_argument(k) for k in self.request.query_arguments}
    body = request_body(route['method'], self.request)
    response = route['handler']({
      'path_params': kwparams,
      'body': body,
      'headers': dict(self.request.headers),
      'query': query})
    status = response.get('status', 200)
    self.set_status(status)
    for k, v in response.get('headers', {}).items():
      self.set_header(k, v)
    self.finish(to_json(response.get('body', {})))
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

model_routes = all_model_routes()

class SwaggerHandler(RequestHandler):
  def get(self):
    self.set_header('Content-Type', 'application/json')
    self.finish(to_json(generate_swagger(model_routes)))

def make_app():
  urls = []
  for path, routes in routes_by_path(model_routes).items():
    urls.append((tornado_path(path), Handler, {'routes': routes}))
  urls.append(('/v1/swagger.json', SwaggerHandler))
  return Application(urls, debug=True)

if __name__ == '__main__':
    app = make_app()
    enable_pretty_logging()
    port = int(os.environ.get('PORT', 5000))
    app.listen(port)
    print(f'tornado starting on port {port}')
    tornado.ioloop.IOLoop.current().start()
