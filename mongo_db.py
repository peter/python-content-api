import os
import pymongo
from bson.objectid import ObjectId

DATABASE_URL = os.environ.get('DATABASE_URL', 'mongodb://localhost:27017/')
client = pymongo.MongoClient(DATABASE_URL)
db = client['python-rest-api']

def count(collection):
  return db[collection].count_documents()

def find(collection):
  return list(db[collection].find({}))

def find_one(collection, id):
  return db[collection].find_one({'_id': ObjectId(id)})

def create(collection, doc):
  result = db[collection].insert_one(doc)
  id = str(result.inserted_id)
  return id

def update(collection, id, doc):
  result = db[collection].find_one_and_replace({'_id': ObjectId(id)}, doc)
  return result

def delete(collection, id):
  result = db[collection].delete_one({'_id': ObjectId(id)})
  # TODO: use result.deleted_count?
  return result
