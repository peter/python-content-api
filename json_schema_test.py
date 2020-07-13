from json_schema import writable_schema

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
