import os
import pymongo
from bson.objectid import ObjectId
from content_api.util import remove_none

DATABASE_URL = os.environ.get('MONGODB_URI', os.environ.get('DATABASE_URL', 'mongodb://localhost:27017/python-rest-api'))
DATABASE_URL += '?retryWrites=false' # This seems to be needed for mlab on Heroku
client = pymongo.MongoClient(DATABASE_URL)
db = client.get_default_database()

def with_id_str(doc):
  if not doc or not '_id' in doc:
    return doc
  return remove_none({**doc, 'id': str(doc['_id']), '_id': None})

def parse_sort(sort):
  if not sort:
    return None
  def parse_item(item):
    name = item[1:] if item.startswith('-') else item
    direction = -1 if item.startswith('-') else 1
    return (name, direction)
  return [parse_item(item) for item in sort.split(',')]

def parse_filter(filter):
  if not filter:
    return None
  def filter_value(v):
    op = 'regex' if v['op'] == 'contains' else v['op']
    return {f'${op}': v['value']}
  return {k: filter_value(v) for k, v in filter.items()}

#############################################################
#
# Database Interface
#
#############################################################

id_json_schema = {'type': 'string', 'pattern': '^[a-z0-9]{24}$', 'x-meta': {'writable': False}}

def count(collection):
  return db[collection].count_documents({})

def find(collection, limit=100, offset=0, sort=None, filter=None):
  print(f'find filter={parse_filter(filter)}')
  return [with_id_str(doc) for doc in list(db[collection].find(limit=limit, skip=offset, sort=parse_sort(sort), filter=parse_filter(filter)))]

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
