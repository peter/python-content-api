from content_api.json_schema import writable_schema, writable_doc

def test_writable_schema():
  schema = {
    'type': 'object',
    'properties': {
      'id': {'type': 'integer', 'x-meta': {'writable': False}},
      'title': {'type': 'string'}
    },
    'required': ['id', 'title']
  }
  expected_schema = {
    'type': 'object',
    'properties': {
      'title': {'type': 'string'}
    },
    'required': ['title']
  }
  assert writable_schema(None) == None
  assert writable_schema({'type': 'string'}) == {'type': 'string'}
  assert writable_schema(schema) == expected_schema

def test_writable_doc():
  schema = {
    'type': 'object',
    'properties': {
      'id': {'type': 'integer', 'x-meta': {'writable': False}},
      'title': {'type': 'string'}
    },
    'required': ['id', 'title']
  }
  doc = {
      'id': 'the-id',
      'title': 'the title'
  }
  expected_doc = {
      'title': 'the title'
  }
  assert writable_doc(schema, None) == None
  assert writable_doc(None, doc) == doc
  assert writable_doc(schema, doc) == expected_doc
