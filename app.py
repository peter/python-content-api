from flask import Flask, jsonify, make_response, request
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

def make_crud_routes(path, model):
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

make_crud_routes('urls', models.urls)
