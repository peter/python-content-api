import os
import pymongo
from bson.objectid import ObjectId
from util import remove_none

DATABASE_URL = os.environ.get('MONGODB_URI', os.environ.get('DATABASE_URL', 'mongodb://localhost:27017/python-rest-api'))
DATABASE_URL += '?retryWrites=false' # This seems to be needed for mlab on Heroku
client = pymongo.MongoClient(DATABASE_URL)
db = client.get_default_database()

def with_id_str(doc):
  if not doc or not '_id' in doc:
    return doc
  return remove_none({**doc, 'id': str(doc['_id']), '_id': None})

#############################################################
#
# Database Interface
#
#############################################################

id_json_schema = {'type': 'string', 'pattern': '^[a-z0-9]{24}$', 'x-meta': {'writable': False}}

def count(collection):
  return db[collection].count_documents({})

def find(collection, limit=100, offset=0):
  return [with_id_str(doc) for doc in list(db[collection].find(limit=limit, skip=offset))]

def find_one(collection, id):
  return with_id_str(db[collection].find_one({'_id': ObjectId(id)}))

def create(collection, doc):
  result = db[collection].insert_one(doc)
  id = str(result.inserted_id)
  return id

def update(collection, id, doc):
  result = db[collection].update_one({'_id': ObjectId(id)}, {'$set': doc})
  # TODO: use result.matched_count or result.modified_count?
  return result

def delete(collection, id):
  result = db[collection].delete_one({'_id': ObjectId(id)})
  # TODO: use result.deleted_count?
  return result
