from flask import Flask, jsonify, make_response, request
import db
from datetime import datetime
import models.urls
from jsonschema import validate, ValidationError

app = Flask(__name__)

@app.errorhandler(ValidationError)
def handle_validation_error(error):
    response = jsonify({'message': error.message, 'schema': error.schema})
    response.status_code = 400
    return response

def not_found_response(message = 'Resource not found'):
    return make_response(jsonify({'message': 'Resource not found'}), 404)

@app.route('/v1/urls', methods = ['GET'])
def urls_list():
    rows = db.query('select * from urls')
    return jsonify(rows)

@app.route('/v1/urls/<int:url_id>', methods = ['GET'])
def urls_get(url_id):
    row = db.query_one("select * from urls where id = %s", [url_id])
    if not row:
        return not_found_response()
    return jsonify(row)

@app.route('/v1/urls', methods = ['POST'])
def urls_create():
    validate(instance=request.json, schema=models.urls.json_schema)
    doc = {**request.json, 'created_at': datetime.now()}
    db.insert('urls', doc)
    # TODO: get id and return created doc: https://stackoverflow.com/questions/5247685/python-postgres-psycopg2-getting-id-of-row-just-inserted
    return jsonify(doc)

@app.route('/v1/urls/<int:url_id>', methods = ['PUT'])
def urls_update(url_id):
    validate(instance=request.json, schema=models.urls.json_schema)
    doc = request.json
    db.update('urls', url_id, doc)
    row = db.query_one("select * from urls where id = %s", [url_id])
    if not row:
        return not_found_response()
    return jsonify(row)

@app.route('/v1/urls/<int:url_id>', methods = ['DELETE'])
def urls_delete(url_id):
    row = db.query_one("select * from urls where id = %s", [url_id])
    if not row:
        return not_found_response()
    db.execute('DELETE from urls where id = %s', [url_id])
    return jsonify({})
