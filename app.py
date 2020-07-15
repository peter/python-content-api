import os
import json
from datetime import date
from flask import Flask, jsonify, make_response, request, redirect, send_from_directory
from util import exception_body
from swagger import generate_swagger
from models import all_model_routes

app = Flask(__name__)

class JsonEncoder(json.JSONEncoder):
	def default(self, obj):
		if isinstance(obj, date): # ISO date formating
			return str(obj)
		return json.JSONEncoder.default(self, obj)

app.json_encoder = JsonEncoder

def flask_response(result):
    return make_response(jsonify(result.get('body', {})), result.get('status', 200))

# Custom generic Flask exception handler (the default is an HTML response)
if not os.environ.get('FLASK_DEBUG', '0'):
    @app.errorhandler(Exception)
    def handle_exception(e):
        return flask_response({'body': exception_body(e), 'status': 500})

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

def make_flask_routes(model_routes):
    def get_flask_handler(route):
        handler = route['handler']
        def list():
            return flask_response(handler())
        def get(id):
            return flask_response(handler(id))
        def create():
            return flask_response(handler(request.json))
        def update(id):
            return flask_response(handler(id, request.json))
        def delete(id):
            return flask_response(handler(id))
        flask_handler = locals()[handler.__name__]
        # See: https://stackoverflow.com/questions/17256602/assertionerror-view-function-mapping-is-overwriting-an-existing-endpoint-functi
        flask_handler.__name__ = f'{route["model"]}_{handler.__name__}'
        return flask_handler
    for route in model_routes:
        app.route(route['path'], methods = [route['method']])(get_flask_handler(route))

model_routes = all_model_routes()
make_flask_routes(model_routes)

@app.route('/')
def redirect_to_swagger():
    return redirect('static/swagger/index.html')

@app.route('/v1/swagger.json')
def swagger_json():
    return jsonify(generate_swagger(model_routes))
