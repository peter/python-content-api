from bottle import Bottle, run, request, response, static_file, redirect, HTTPResponse
import os
import json
from datetime import date
from swagger import generate_swagger
from models import all_model_routes

app = Bottle()

class JsonEncoder(json.JSONEncoder):
	def default(self, obj):
		if isinstance(obj, date): # ISO date formating
			return str(obj)
		return json.JSONEncoder.default(self, obj)

def bottle_response(model_response):
    headers = {'Content-type': 'application/json'}
    status = model_response.get('status', 200)
    body = json.dumps(model_response.get('body', {}), indent=4, cls=JsonEncoder)
    response.status = status
    response.set_header('Content-Type', 'application/json')
    for k, v in model_response.get('headers', {}).items():
        response.set_header(k, v)
    return body
    #return HTTPResponse(status=status, body=body, headers=headers)

def make_bottle_routes(model_routes):
    pass
    def generate_bottle_handler(route):
        handler = route['handler']
        @app.route(route['path'], method = [route['method']])
        def bottle_handler(**kwargs):
            return bottle_response(handler(
                path_params=kwargs,
                data=request.json,
                headers=dict(request.headers),
                query=dict(request.query)))
        bottle_handler.__name__ = f'{route["model_name"]}_{route["name"]}'
    for route in model_routes:
        generate_bottle_handler(route)

model_routes = all_model_routes()
make_bottle_routes(model_routes)

@app.route('/static/<filename:path>')
def server_static(filename):
    return static_file(filename, root='static')

@app.route('/v1/swagger.json')
def swagger_json():
    return bottle_response({'body': generate_swagger(model_routes)})

@app.route('/')
def redirect_to_swagger():
    return redirect('/static/index.html')

if __name__ == '__main__':
  # Development server
  port = int(os.environ.get('PORT', 5000))
  run(app, host='localhost', port=port, debug=True, reloader=True)
