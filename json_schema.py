from jsonschema import validate, ValidationError

def validate_schema(instance, schema):
  try:
    validate(instance=instance, schema=schema)
    return None
  except ValidationError as schema_error:
    return schema_error

def validate_response(schema_error):
  body = {'error': {'message': schema_error.message, 'schema': schema_error.schema}}
  return {'status': 400, 'body': body}
