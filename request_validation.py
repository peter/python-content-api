from json_schema import validate_schema, schema_error_response, writable_schema, writable_doc
from util import get, invalid_response

def parameters_schema(parameters, source):
  properties = {p['name']: p.get('schema') for p in parameters if p.get('schema')}
  if not properties:
    return None
  required = [p['name'] for p in parameters if p.get('required') == True]
  additional_properties = True if source == 'header' else False
  return {
    'type': 'object',
    'properties': properties,
    'required': required,
    'additionalProperties': additional_properties
  }

def coerce_values(values, schema):
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
      else:
        return value
    except:
      return value
  return {k: coerce_value(v, get(schema, f'properties.{k}')) for k, v in values.items()}

def validate_parameters(route, **kwargs):
  if 'parameters' not in route:
    return None
  sources = {'query': 'query', 'path': 'path_params', 'header': 'headers'}
  for source, arg_name in sources.items():
    parameters_in = [p for p in route['parameters'] if p['in'] == source]
    schema = parameters_schema(parameters_in, source)
    if schema:
      values = coerce_values(kwargs.get(arg_name, {}), schema)
      schema_error = validate_schema(values, schema)
      if schema_error:
        return schema_error

def decorate_handler_with_validation(route):
  def handler_with_validation(**kwargs):
    schema_error = validate_parameters(route, **kwargs)
    if schema_error:
      return schema_error_response(schema_error)
    data_schema = route.get('request_schema')
    if data_schema:
      write_schema = writable_schema(data_schema)
      data = writable_doc(data_schema, kwargs.get('data'))
      schema_error = validate_schema(data, write_schema)
      if schema_error:
        return schema_error_response(schema_error)
    return route['handler'](**kwargs)
  handler_with_validation.__name__ = f'{route["handler"].__name__}_with_validation'
  return handler_with_validation
