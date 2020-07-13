from jsonschema import validate, ValidationError
from util import get

def validate_schema(instance, schema):
  try:
    validate(instance=instance, schema=schema)
    return None
  except ValidationError as schema_error:
    return schema_error

def is_writable(property):
  return get(property, 'x-meta.writable') != False

def writable_schema(schema):
  if not schema or not 'properties' in schema:
    return schema
  properties = {key: property for key, property in schema['properties'].items() if is_writable(property)}
  get_required = lambda required: [key for key in required if key in properties]
  return {
    **schema,
    'properties': properties,
    'required': (schema['required'] and get_required(schema['required']))
  }

def validate_response(schema_error):
  body = {'error': {'message': schema_error.message, 'schema': schema_error.schema}}
  return {'status': 400, 'body': body}
