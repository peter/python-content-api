from util import named_args

ARTICLES = [
  {
    'title': 'Why are so many corona patients struggling with lingering symptoms?'
  },
  {
    'title': 'Lionel Messi labels Barcelona a "weak" team following shock defeat'
  }
]

PREMIUM_ARTICLES = [
  {
    'title': 'Many people don\'t know their blood type. Here\'s how to find out yours'
  }
]

json_schema = {
  'type': 'object',
  'properties': {
    'title': {'type': 'string'}
  },
  'additionalProperties': False,
  'required': ['title']
}

@named_args
def list_articles(query, headers, **request):
  def is_match(article):
    return 'q' not in query or query['q'].lower() in article['title'].lower()
  articles = ARTICLES
  if headers.get('Authorization') == 'secret':
    articles = articles + PREMIUM_ARTICLES
  data = [a for a in articles if is_match(a)]
  return {'body': {'data': data}}

@named_args
def create_articles(data, **request):
  ARTICLES.append(data)
  return {'body': data}

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
        'schema': {'type': 'string', 'minLength': 2}
      },
      {
        'in': 'header',
        'name': 'Authorization',
        'description': 'Auth key for premium access',
        'schema': {'type': 'string', 'minLength': 6, 'maxLength': 6}
      }
    ]
  },
  {
    'method': 'POST',
    'path': '/v1/articles',
    'handler': create_articles,
    'request_schema': json_schema
  }
]
