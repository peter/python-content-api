# Example Python REST API

## Features

* Minimal codebase - around 500 lines of Python (see [bin/loc](bin/loc))
* Postgresql access with psycopg2 (see [db/pg.py](db/pg.py))
* MongoDB access with pymongo (see [db/mongodb.py](db/mongodb.py))
* Generic CRUD model API that is easy to adapt to Flask or serverless etc. (see [model_api.py](model_api.py) and [models/__init__.py](models/__init__.py) and example models like [models/urls.py](models/urls.py) and [models/users.py](models/users.py))
* Flask CRUD API (a thin wrapper around the model API, see [flask_app.py](flask_app.py) and [model_routes.py](model_routes.py)). There is also support for Bottle in [bottle_app.py](bottle_app.py) and Tornado in [tornado_app.py](tornado_app.py). With both Bottle and Tornado I had issues with internal URLs, i.e. where the server would make requests back to itself. Once I changed [app_test.py](app_test.py) to use external URLs this was resolved.
* Validation with jsonschema (see the `validate_schema` function in [json_schema.py](json_schema.py) and its usages in [request_validation.py](request_validation.py), and [app_test.py](app_test.py))
* API testing with pytest and the request package (see [app_test.py](app_test.py))
* OpenAPI/Swagger documentation generated from model routes (see [swagger.py](swagger.py))
* Deployment to Heroku
* Deployment with Zappa to AWS Lambda

TODO:

* Try running Mongodb on Heroku (use MONGODB_URI if available and set DATABASE=mongodb)
* Unique constraint for mongodb
* List endpoint should support page, limit, and filter params

Some alternatives for building an API like this in Python with popular frameworks:

* [Flask](https://flask.palletsprojects.com) + [SQLAlchemy](https://www.sqlalchemy.org/) + (possibly) [OpenAPI-SQLAlchemy](https://pypi.org/project/OpenAPI-SQLAlchemy)
* [Django REST Framework](https://www.django-rest-framework.org/)

## Demo App

[python-heroku-rest-api.herokuapp.com](https://python-heroku-rest-api.herokuapp.com)

## Models, Routes, and Handlers

* If a model doesn't specify a `routes` attribute then it will get the five default CRUD routes (`list`, `get`, `create`, `update`, `delete`) based on the models `json_schema` and `db_schema` attributes (those need to be present). For examples see [models/fetches.py](models/fetches.py). If you only want to expose a subset of the CRUD routes for a model you can set the `route_names` attribute, see [models/users.py](models/users.py)
* By specifying the `routes` property for a model you can customize the default CRUD routes, for example to add custom validation, see [models/urls.py](models/urls.py). You are also free to set any types of routes that you need for the model and the `json_schema` and `db_schema` properties are not required in this case. You may for example have a model that uses a different database or no database at all, see [models/articles.py](models/articles.py). The `routes` property needs to be a list of dictionaries with the keys `method`, `path`, `handler`, and the optional keys `name` (name of the route, defaults to the name of handler function), `request_schema` (JSON schema to validate in request body), `response_schema` (JSON schema of response body), and `parameters` (a list of [OpenAPI parameters](https://swagger.io/docs/specification/describing-parameters/) to validate in path/query/header - see [models/articles.py](models/articles.py)). The default CRUD routes are defined in [model_routes.py](model_routes.py).

A route `handler` will receive a single argument `request` dict with these attributes:

* `path_params` - dict with parameters from the path, such as `id` for `/v1/urls/<id>`
* `body` - dict with body data for `POST` and `PUT` requests
* `headers` - dict with HTTP request headers
* `query` - dict with query parameters, such as `{'page': 2}` for `/v1/articles?page=2`

If you prefer you can use the `@named_args` decorator to unpack the request dict and have your handler receive the request attributes as named arguments, see [models/articles.py](models/articles.py).

A route `handler` returns a `response` dict with these attributes:

* `body` - data to be JSON serialized
* `status` (optional) - HTTP status code (defaults to 200)
* `headers` (optional) - a dict with HTTP response headers

## Decorators

What's usually referred to as `middleware` in web frameworks can be achieved
by adding [Python decorators](https://www.programiz.com/python-programming/decorator) to
a route `handler`, see for example how this is done in [model_api.py](model_api.py) and
in [models/__init__.py](models/__init__.py) or in this simple example model (notice that the order of decorators potentially matters):

```python
from functools import wraps
import time

def with_headers(response, headers):
  return {**response, 'headers': {**response.get('headers', {}), **headers}}

def timer(handler):
  @wraps(handler)
  def with_timer(request):
    start_time = time.time()
    response = handler(request)
    elapsed = round((time.time() - start_time)*1000, 3)
    return with_headers(response, {'X-Response-Time': f'{elapsed}ms'})
  return with_timer

def cache_header(handler):
  @wraps(handler)
  def with_cache_header(request):
    response = handler(request)
    return with_headers(response, {'Cache-Control': 'max-age=120'})
  return with_cache_header

@timer
@cache_header
def decorators_example(request):
  return {'body': {}}

routes = [
  {
    'path': '/v1/decorators_example',
    'handler': decorators_example
  },
]
```

Note that the `@wraps` decorator in the code above is not strictly necessary
but its main purpose is to preserve the name of the handler function, i.e. it
makes sure that `decorators_example.__name__` doesn't change.

Composing decorators is fairly straightforward, see [models/composed_decorators_example.py](models/composed_decorators_example.py).

## Setting up the Development Environment

Install packages in a virtual env:

```sh
python -m venv venv
. venv/bin/activate
pip install -r requirements.txt
```

Create database:

```sh
createdb -U postgres python-rest-api
python -c "import models; models.create_schema()"
```

Start a Flask server:

```sh
bin/start-dev

open http://localhost:5000
```

Use the `FRAMEWORK` env variable to start using a different web framework:

```sh
FRAMEWORK=bottle bin/start-dev
FRAMEWORK=tornado bin/start-dev
```

## Running the API tests

```sh
FRAMEWORK=flask bin/test
FRAMEWORK=bottle bin/test
FRAMEWORK=tornado bin/test
```

To run the API tests against mongodb:

```sh
DATABASE=mongodb bin/test
```

The API tests can be run against the Heroku demo app as well:

```sh
BASE_URL=https://python-heroku-rest-api.herokuapp.com pytest -s -vv app_test.py
```

## API Documentation (OpenAPI/Swagger)

Interactive HTML docs:

```sh
open http://localhost:5000/static/swagger/index.html
```

OpenAPI specification:

```sh
open http://localhost:5000/v1/swagger.json
```

## Invoking the API

Below is an example of testing the CRUD operations of the API from the command line using `curl` and [jq](https://stedolan.github.io/jq/) (`brew install jq`):

```sh
export BASE_URL=http://localhost:5000

# create with invalid data yields 400
curl -i -H "Content-Type: application/json" -X POST -d '{"url":"http://www.google.com", "foo": 1}' $BASE_URL/v1/urls

# successful create
export URL=$(curl -H "Content-Type: application/json" -X POST -d '{"url":"http://www.google.com"}' $BASE_URL/v1/urls)
export ID=$(echo $URL | jq --raw-output '.id')

# list
curl -i $BASE_URL/v1/urls

# get of non-existant id yields 404
curl -i $BASE_URL/v1/urls/12345

# get
curl -i $BASE_URL/v1/urls/$ID

# update of non-existant id yields 404
curl -i -H "Content-Type: application/json" -X PUT -d '{"url":"http://www.yahoo.com"}' $BASE_URL/v1/urls/12345

# update with invalid data yields 400
curl -i -H "Content-Type: application/json" -X PUT -d '{"url":"http://www.yahoo.com", "foo": 1}' $BASE_URL/v1/urls/$ID

# successful update
curl -i -H "Content-Type: application/json" -X PUT -d '{"url":"http://www.yahoo.com"}' $BASE_URL/v1/urls/$ID

# Check the update happened
curl -i $BASE_URL/v1/urls
curl -i $BASE_URL/v1/urls/$ID

# delete of non-existant id yields 404
curl -i -X DELETE $BASE_URL/v1/urls/12345

# successful delete
curl -i -X DELETE $BASE_URL/v1/urls/$ID

# Check the delete happened
curl -i $BASE_URL/v1/urls
curl -i $BASE_URL/v1/urls/$ID
```

## Talking to Postgres

From python:

```sh
python
import db.pg as db
from datetime import datetime

# create
db.execute('INSERT INTO urls (url, created_at) VALUES (%s, %s)', ("http://www.aftonbladet.se", datetime.now()))

# list
db.query("select * from urls")

# get
db.query_one("select * from urls where id = %s", [1])

# update
db.execute('UPDATE urls SET url = %s where id = %s', ("http://www.expressen.se", 1))

# delete
db.execute('DELETE from urls where id = %s', [1])
```

Connecting with psql:

```
psql -U postgres python-rest-api

delete from urls;
```

## Talking to MongoDB

```sh
python
import db.mongodb as db
from datetime import datetime

# create
id = db.create('urls', {'url': 'http://www.aftonbladet.se', 'created_at': datetime.now()})

# list
db.find('urls')

# get
url = db.find_one('urls', id)

# update
db.update('urls', id, {**url, 'url': 'http://www.expressen.se'})

# delete
db.delete('urls', id)
```

Connecting with the Mongo shell:

```sh
mongo python-rest-api

db.urls.find()
db.urls.remove({})
```

## How this app was created

Create and activate virtual python env:

```sh
python -m venv venv
echo 'venv' > .gitignore
. venv/bin/activate
```

Add packages and freeze them in requirements.txt:

```sh
pip install gunicorn Flask psycopg2 requests
pip freeze > requirements.txt
```

Create database:

```sh
createdb python-heroku-starter
```

Create script `bin/start-dev` and basic `app.py`.

Push files to git:

```sh
git add .
git commit -m 'hello world'
git push origin master
```

## Deployment with Heroku

Specify Python version and Procfile for Heroku:

```sh
python --version # => Python 3.7.7
echo 'python-3.7.7' > runtime.txt
echo 'web gunicorn app:app' > Procfile
```

Create heroku app:

```sh
heroku apps:create --region eu python-rest-api
```

Deploy:

```sh
git push heroku master
```

Add the [heroku-postgresql addon](https://elements.heroku.com/addons/heroku-postgresql):

```sh
heroku addons:create heroku-postgresql:hobby-dev
```

For MongoDB you can use the [mongolab addon](https://elements.heroku.com/addons/mongolab):

```sh
heroku addons:create mongolab:sandbox
```

Test the app:

```sh
heroku open
```

## Deployment with Zappa to AWS Lambda

Make sure you have an AWS account and set up a user with programmatic access in the AWS console. Add the keys to `~/.aws/credentials`:

```
[default]
aws_access_key_id = ...
aws_secret_access_key = ...
```

Install Zappa:

```sh
pip install zappa
pip freeze > requirements.txt
```

[Recreate the virtual env](https://github.com/Miserlou/Zappa/issues/1232):

```sh
deactivate
rm -rf ./venv
python -m venv venv
. venv/bin/activate
pip install -r requirements.txt
```

```sh
zappa init
```

The `zappa init` command will create a `zappa_settings.json` file like the following (where I think I needed to add the `aws_region` manually):

```json
{
    "production": {
        "app_function": "app.app",
        "profile_name": "private",
        "aws_region": "eu-north-1",
        "project_name": "python-rest-api",
        "runtime": "python3.8",
        "s3_bucket": "zappa-python-rest-api"
    }
}
```

Deploy:

```sh
zappa deploy production
```

Zappa error: [Status check on the deployed lambda failed](https://github.com/Miserlou/Zappa/issues/1985), see also [Error loading psycopg2 module](https://github.com/Miserlou/Zappa/issues/800). *NOTE: in order to get Zappa deployment to work I needed to replace the `psycopg2` package with [psycopg2-binary](https://pypi.org/project/psycopg2-binary) and "the binary package is a practical choice for development and testing but in production it is advised to use the package built from sources"*.

Zappa debug logs:

```sh
zappa tail
```

I used the AWS console for lambda to set the DATABASE_URL [env variable](https://github.com/Miserlou/Zappa#setting-environment-variables) for the Heroku app.

Issue: the AWS lambda app is deployed at a URL like `https://779tuhzuhc.execute-api.eu-north-1.amazonaws.com/production` i.e. it is not deployed at the root path but at `/production`. This breaks the swagger UI.

To re-deploy zappa:

```sh
zappa update production
```

The API tests can be run against the deployed app like so:

```sh
BASE_URL=https://779tuhzuhc.execute-api.eu-north-1.amazonaws.com/production python -m pytest -s app_test.py
```

## Resources

* [Installing Postgres via Brew on Mac](https://gist.github.com/ibraheem4/ce5ccd3e4d7a65589ce84f2a3b7c23a3)
* [Python Flask/Auth/Heroku Example app](https://github.com/peter/api-auth-examples/tree/master/flask)
* [Getting Started on Heroku with Python](https://devcenter.heroku.com/articles/getting-started-with-python?singlepage=true)
* [Deploying Python Applications with Gunicorn (Heroku)](https://devcenter.heroku.com/articles/python-gunicorn)
* [Gunicorn homepage](https://gunicorn.org)
* [Specifying a Python Runtime](https://devcenter.heroku.com/articles/python-runtimes)
* [Most Popular Python Packages](https://pypistats.org/top)
* [Bottle Web Framework (alternative to Flask)](https://bottlepy.org/docs/dev/)
* [Swagger UI](https://swagger.io/docs/open-source-tools/swagger-ui/usage/installation)
* [OpenAPI 3 Meta Schema](https://github.com/OAI/OpenAPI-Specification/tree/master/schemas/v3.0)
* [ReDoc - API Console feature request](https://github.com/Redocly/redoc/issues/53)
* [Redoc.ly Developer Portal (Commercial)](https://redoc.ly/developer-portal)
* [How to build a REST API with Tornado](https://medium.com/octopus-labs-london/how-to-build-a-rest-api-in-python-with-tornado-fc717c33824a)
* [MongoDB Tutorial](https://pymongo.readthedocs.io/en/stable/tutorial.html)
* [MongoDB Collection Operations](https://pymongo.readthedocs.io/en/stable/api/pymongo/collection.html)

Serverless (AWS Lambda) deployment:

* [Chalice - Serverless Python](https://realpython.com/aws-chalice-serverless-python/)
* [AWS Lambda with Python - Simple Example](https://www.scalyr.com/blog/aws-lambda-with-python/)
* [AWS Lambda with Python - Getting Started Guide](https://stackify.com/aws-lambda-with-python-a-complete-getting-started-guide/)
* [The Official Guide to Serverless Flask](https://www.serverless.com/flask)
