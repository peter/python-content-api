from content_api.json_schema import validate_schema, schema_error_response, writable_schema, writable_doc, coerce_values
from content_api.util import get, invalid_response
from functools import wraps

def parameters_schema(parameters, source):
  properties = {p['name']: p.get('schema') for p in parameters if p.get('schema') and not get(p, 'x-meta.namePattern')}
  if not properties:
    return None
  pattern_properties = {get(p, 'x-meta.namePattern'): p.get('schema') for p in parameters if get(p, 'x-meta.namePattern')}
  required = [p['name'] for p in parameters if p.get('required') == True]
  additional_properties = True if source == 'header' else False
  return {
    'type': 'object',
    'properties': properties,
    'patternProperties': pattern_properties,
    'required': required,
    'additionalProperties': additional_properties
  }

def validate_parameters(route, request):
  if 'parameters' not in route:
    return None
  sources = {'query': 'query', 'path': 'path_params', 'header': 'headers'}
  for source, arg_name in sources.items():
    parameters_in = [p for p in route['parameters'] if p['in'] == source]
    schema = parameters_schema(parameters_in, source)
    if schema:
      values = coerce_values(request.get(arg_name, {}), schema)
      schema_error = validate_schema(values, schema)
      if schema_error:
        return schema_error

def decorate_handler_with_validation(route):
  @wraps(route['handler'])
  def handler_with_validation(request):
    schema_error = validate_parameters(route, request)
    if schema_error:
      return schema_error_response(schema_error)
    data_schema = route.get('request_schema')
    if data_schema:
      write_schema = writable_schema(data_schema)
      data = writable_doc(data_schema, request.get('body'))
      schema_error = validate_schema(data, write_schema)
      if schema_error:
        return schema_error_response(schema_error)
    return route['handler'](request)
  return handler_with_validation
