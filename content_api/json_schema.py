from jsonschema import validate, ValidationError
from content_api.util import get
from dateutil.parser import parse as parse_date

def validate_schema(instance, schema):
  try:
    validate(instance=instance, schema=schema)
    return None
  except ValidationError as schema_error:
    return schema_error

def coerce_value(value, value_schema):
  value_type = get(value_schema, 'type')
  if not value_type or value is None:
    return value
  try:
    if value_type == 'integer' or (value_type == 'number' and '.' not in value):
      return int(value)
    elif value_type == 'number' and '.' in value:
      return float(value)
    elif value_type == 'boolean':
      return value not in ['0', 'false', 'FALSE', 'f']
    elif value_type == 'string' and get(value_schema, 'format') == 'date-time':
      return parse_date(value)
    else:
      return value
  except:
    return value

def coerce_values(values, schema):
  return {k: coerce_value(v, get(schema, f'properties.{k}')) for k, v in values.items()}

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

def writable_doc(schema, doc):
  if not doc or not schema or not 'properties' in schema:
    return doc
  unwritable_keys = [k for k, v in schema['properties'].items() if not is_writable(v)]
  return {k: v for k, v in doc.items() if k not in unwritable_keys}

def schema_error_response(schema_error):
  body = {'error': {'message': schema_error.message, 'path': list(schema_error.path), 'schema': schema_error.schema}}
  return {'status': 400, 'body': body}
