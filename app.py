from flask import Flask, jsonify, make_response, request
import models.urls

app = Flask(__name__)

# TODO: status 500 handler that returns JSON

def flask_response(result):
    return make_response(jsonify(result.get('body', {})), result.get('status', 200))

@app.route('/v1/urls', methods = ['GET'])
def urls_list():
    return flask_response(models.urls.list())

@app.route('/v1/urls/<int:url_id>', methods = ['GET'])
def urls_get(url_id):
    return flask_response(models.urls.get(url_id))

@app.route('/v1/urls', methods = ['POST'])
def urls_create():
    return flask_response(models.urls.create(request.json))

@app.route('/v1/urls/<int:url_id>', methods = ['PUT'])
def urls_update(url_id):
    return flask_response(models.urls.update(url_id, request.json))

@app.route('/v1/urls/<int:url_id>', methods = ['DELETE'])
def urls_delete(url_id):
    return flask_response(models.urls.delete(url_id))
