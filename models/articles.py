ARTICLES = [
  {
    'title': 'Why are so many corona patients struggling with lingering symptoms?'
  },
  {
    'title': 'Lionel Messi labels Barcelona a "weak" team following shock defeat'
  }
]

def list_articles(query, headers, **kwargs):
  print(f'query={query}')
  print(f'headers={headers}')
  def is_match(article):
    return 'q' not in query or query['q'].lower() in article['title'].lower()
  data = [a for a in ARTICLES if is_match(a)]
  return {'body': {'data': data}}

routes = [
  {
    'method': 'GET',
    'path': '/v1/articles',
    'handler': list_articles,
    'parameters': [
      {
        'in': 'query',
        'name': 'q',
        'description': 'Search query to filter by',
        'schema': {'type': 'string'}
      }
    ]
  }
]
