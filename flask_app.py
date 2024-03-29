import os
import json
from datetime import date
from flask import Flask, jsonify, make_response, request, redirect, send_from_directory
from content_api.util import exception_body
from content_api.swagger import generate_swagger
from content_api.models import all_model_routes

app = Flask(__name__)

class JsonEncoder(json.JSONEncoder):
	def default(self, obj):
		if isinstance(obj, date): # ISO date formating
			return str(obj)
		return json.JSONEncoder.default(self, obj)

app.json_encoder = JsonEncoder

def flask_response(result):
    # response = app.response_class(response=jsonify(result.get('body', {})),
    #                               status=result.get('status', 200),
    #                               mimetype='application/json')
    response = make_response(jsonify(result.get('body', {})), result.get('status', 200))
    for k, v in result.get('headers', {}).items():
        response.headers[k] = v
    return response

# Custom generic Flask exception handler (the default is an HTML response)
if not os.environ.get('FLASK_DEBUG', '0'):
    @app.errorhandler(Exception)
    def handle_exception(e):
        return flask_response({'body': exception_body(e), 'status': 500})

def make_flask_routes(model_routes):
    def get_flask_handler(index, route):
        handler = route['handler']
        def flask_handler(**kwargs):
            return flask_response(handler({
                'path_params': kwargs,
                'body': request.json if request.is_json else None,
                'headers': dict(request.headers),
                'query': dict(request.args)}))
        # Flask handler names need to be uniqe, see: https://stackoverflow.com/questions/17256602/assertionerror-view-function-mapping-is-overwriting-an-existing-endpoint-functi
        flask_handler.__name__ = f'{route["model_name"]}_{route["name"]}_{index}'
        return flask_handler
    for index, route in enumerate(model_routes):
        print(route['method'], route['path'])
        app.route(route['path'], methods = [route['method']])(get_flask_handler(index, route))

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('./static', path)

model_routes = all_model_routes()
make_flask_routes(model_routes)

@app.route('/')
def redirect_to_swagger():
    return redirect('/static/index.html')

@app.route('/v1/swagger.json')
def swagger_json():
    return jsonify(generate_swagger(model_routes))
