from flask import Flask, jsonify, make_response, request
from model_api import make_model_api
import models.urls

app = Flask(__name__)

def flask_response(result):
    return make_response(jsonify(result.get('body', {})), result.get('status', 200))

# Custom generic Flask exception handler (the default is an HTML response)
@app.errorhandler(Exception)
def handle_exception(e):
    body = {
        'error': {
            'type': type(e).__name__,
            'message': (e.args[0] if e.args else None)
        }
    }
    return flask_response({'body': body, 'status': 500})

def make_flask_routes(path, model):
    @app.route(f'/v1/{path}', methods = ['GET'])
    def list():
        return flask_response(model.list())

    @app.route(f'/v1/{path}/<int:id>', methods = ['GET'])
    def get(id):
        return flask_response(model.get(id))

    @app.route(f'/v1/{path}', methods = ['POST'])
    def create():
        return flask_response(model.create(request.json))

    @app.route(f'/v1/{path}/<int:id>', methods = ['PUT'])
    def update(id):
        return flask_response(model.update(id, request.json))

    @app.route(f'/v1/{path}/<int:id>', methods = ['DELETE'])
    def delete(id):
        return flask_response(model.delete(id))

models = {
    'urls': models.urls.json_schema
}

for table_name, json_schema in models.items():
    model = make_model_api(table_name, json_schema)
    make_flask_routes(table_name, model)
