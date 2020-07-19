import re

# Covert /v1/foobar/<id> to /v1/foobar/{id}
def swagger_path(route_path):
  return re.sub(r'<([a-zA-Z0-9_]+)>', '{\\1}', route_path)

def swagger_parameters(route):
  return route['parameters'] if 'parameters' in route else []

def swagger_request_body(route):
  if not route['request_schema']:
    return None
  return {
        'content': {
            'application/json': {
                'schema': route['request_schema']
            }
        }
    }

def swagger_responses(route):
  responses = {'200': {'description': 'success'}}
  if 'response_schema' in route:
    responses['200']['content'] = {
          'application/json': {
              'schema': route['response_schema']
          }
      }
  if route['method'] == 'PUT' or route['method'] == 'POST':
    responses['400'] = {'description': 'validation failure'}
  return responses

def swagger_paths(model_routes):
  paths = {}
  for route in model_routes:
    path = swagger_path(route['path'])
    if not path in paths:
      paths[path] = {}
    method = route['method'].lower()
    summary = f'{route["model_name"]}: {route["name"]}'
    swaggerPath = {
      'tags': [route['model_name']],
      'summary': summary,
      'parameters': swagger_parameters(route),
      'responses': swagger_responses(route)
    }
    if 'request_schema' in route:
      swaggerPath['requestBody'] = swagger_request_body(route)
    paths[path][method] = swaggerPath
  return paths

def generate_swagger(model_routes):
  return {
    'openapi': '3.0.1',
    'info': {
      'description': 'An example Python REST API on Heroku with postgresql, Flask, JSON schema validation etc.',
      'version': '1.0.0',
      'title': 'Example Python REST API'
    },
    'paths': swagger_paths(model_routes)
  }
