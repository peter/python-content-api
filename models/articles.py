ARTICLES = [
  {
    'title': 'Why are so many corona patients struggling with lingering symptoms?'
  }
]

def list_articles(query, headers, **kwargs):
  print(f'query={query}')
  print(f'headers={headers}')
  return {'body': {'data': ARTICLES}}

routes = [
  {
    'method': 'GET',
    'path': '/v1/articles',
    'handler': list_articles,
    'model': 'articles'
  }
]
