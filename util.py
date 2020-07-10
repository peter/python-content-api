def exception_body(exception):
  return {
        'error': {
            'type': type(exception).__name__,
            'message': (exception.args[0] if exception.args else None)
        }
    }
