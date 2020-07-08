from flask import Flask, jsonify, abort, request
import db
from datetime import datetime

app = Flask(__name__)

@app.route('/v1/urls', methods = ['GET'])
def urls_list():
    rows = db.query('select * from urls')
    return jsonify(rows)

@app.route('/v1/urls/<int:url_id>', methods = ['GET'])
def urls_get(url_id):
    row = db.query_one("select * from urls where id = %s", [url_id])
    if not row:
        abort(404)
    return jsonify(row)

@app.route('/v1/urls', methods = ['POST'])
def urls_create():
    # TODO: proper validation
    # TODO: whitelist column names, SQL injection risk
    if not request.json or not 'url' in request.json:
        abort(400)
    doc = {**request.json, 'created_at': datetime.now()}
    db.insert('urls', doc)
    # TODO: get id and return created doc: https://stackoverflow.com/questions/5247685/python-postgres-psycopg2-getting-id-of-row-just-inserted
    return jsonify(doc)

@app.route('/v1/urls/<int:url_id>', methods = ['PUT'])
def urls_update(url_id):
    # TODO: proper validation
    # TODO: whitelist column names, SQL injection risk
    if not request.json or not 'url' in request.json:
        abort(400)
    doc = request.json
    db.update('urls', url_id, doc)
    row = db.query_one("select * from urls where id = %s", [url_id])
    return jsonify(row)

@app.route('/v1/urls/<int:url_id>', methods = ['DELETE'])
def urls_delete(url_id):
    row = db.query_one("select * from urls where id = %s", [url_id])
    if not row:
        abort(404)
    db.execute('DELETE from urls where id = %s', [url_id])
    return jsonify({})
