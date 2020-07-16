ARTICLES = [
  {
    'title': 'Why are so many corona patients struggling with lingering symptoms?'
  }
]

def list():
  return {'body': {'data': ARTICLES}}

routes = [
  {
    'method': 'GET',
    'path': '/v1/articles',
    'handler': list,
    'model': 'articles'
  }
]
