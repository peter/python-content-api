import re

def invalid_response(message):
  return {'body': {'error': {'message': message}}, 'status': 400}

def exception_body(exception):
  return {
        'error': {
            'type': type(exception).__name__,
            'message': (exception.args[0] if exception.args else None)
        }
    }

def exception_response(error):
    return {'body': exception_body(error), 'status': 400}

def get(value, keys, default_value = None):
    '''
        Useful for reaching into nested JSON like data
        Inspired by JavaScript lodash get and Clojure get-in etc.
        Similar to https://github.com/dgilland/pydash get
    '''
    if value is None or keys is None:
        return None
    path = keys.split('.') if isinstance(keys, str) else keys
    result = value
    def valid_index(key):
        return re.match('^([1-9][0-9]*|[0-9])$', key) and int(key) >= 0
    def is_dict_like(v):
        return hasattr(v, '__getitem__') and hasattr(v, '__contains__')
    for key in path:
        if isinstance(result, list) and valid_index(key) and int(key) < len(result):
            result = result[int(key)] if int(key) < len(result) else None
        elif is_dict_like(result) and key in result:
            result = result[key]
        else:
            result = default_value
            break
    return result

def omit(d, keys):
     return {k: d[k] for k in d if k not in keys}

def pick(d, keys):
     return {k: d[k] for k in d if k in keys}
