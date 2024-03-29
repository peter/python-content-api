# Python Content API

An example Python CRUD (REST) API framework. The idea is that you define models (see [users model](models/users.py)) with JSON and database schema (for PostgreSQL) and the framework then takes care of exposing get/list/create/update/delete endpoints for you with validation and OpenAPI documentation.

## Setting up the Development Environment

Those instructions were tested with Python 3.11.6.

Install packages in a virtual env:

```sh
python -m venv venv
. venv/bin/activate
pip install -r requirements.txt
```

Create database:

```sh
createuser -s postgres # fixes role "postgres" does not exist
createdb -U postgres python-rest-api
python -c "import content_api.models as models; models.create_schema()"
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

Run the tests:

```sh
FRAMEWORK=flask bin/test
```

To recreate the virtual environment:

```sh
deactivate
rm -rf ./venv
python -m venv venv
. venv/bin/activate
pip install -r requirements.txt
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

# list - pagination
curl -i "$BASE_URL/v1/urls?offset=1&limit=50"

# list - sorting
curl -i "$BASE_URL/v1/urls?sort=created_at"

# list - filtering
curl -gi "$BASE_URL/v1/urls?filter.url=http://www.google.com"
curl -gi "$BASE_URL/v1/urls?filter.url[contains]=google"
curl -gi "$BASE_URL/v1/urls?filter.created_at[lt]=2023-12-02"

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

## Features

* A microframework for content APIs with minimal codebase - less than 1000 lines of Python (see the [content_api](content_api) directory and [bin/loc](bin/loc))
* Postgresql access with psycopg2 (see [db/pg.py](content_api/db/pg.py))
* MongoDB access with pymongo (see [db/mongodb.py](content_api/db/mongodb.py))
* Generic CRUD model API that is easy to adapt to Flask or serverless etc. (see [model_api.py](content_api/model_api.py) and [models.py](content_api/models.py) and example models like [urls](models/00_urls.py) and [users](models/users.py))
* Flask CRUD API (a thin wrapper around the model API, see [flask_app.py](flask_app.py) and [model_routes.py](content_api/model_routes.py)). There is also support for Bottle in [bottle_app.py](bottle_app.py) and Tornado in [tornado_app.py](tornado_app.py). With both Bottle and Tornado I had issues with internal URLs, i.e. where the server would make requests back to itself. Once I changed [app_test.py](content_api/app_test.py) to use external URLs this was resolved.
* Validation with jsonschema (see the `validate_schema` function in [json_schema.py](content_api/json_schema.py) and its usages in [request_validation.py](content_api/request_validation.py), and [app_test.py](content_api/app_test.py))
* API testing with pytest and the request package (see [app_test.py](content_api/app_test.py))
* OpenAPI/Swagger documentation generated from model routes (see [swagger.py](content_api/swagger.py))
* Deployment to Heroku

Some alternatives for building an API like this in Python with popular frameworks:

* [FastAPI](https://fastapi.tiangolo.com)
* [Flask](https://flask.palletsprojects.com) + [SQLAlchemy](https://www.sqlalchemy.org/) + (possibly) [OpenAPI-SQLAlchemy](https://pypi.org/project/OpenAPI-SQLAlchemy)
* [Django REST Framework](https://www.django-rest-framework.org/)

## Demo App

[python-rest-api-112f9b8f7887.herokuapp.com](https://python-rest-api-112f9b8f7887.herokuapp.com)

## Models, Routes, and Handlers

* If a model doesn't specify a `routes` attribute then it will get the five default CRUD routes (`list`, `get`, `create`, `update`, `delete`) based on the models `json_schema` and `db_schema` attributes (those need to be present). For examples see [models/00_fetches.py](models/00_fetches.py). If you only want to expose a subset of the CRUD routes for a model you can set the `route_names` attribute, see [models/users.py](models/users.py)
* By specifying the `routes` property for a model you can customize the default CRUD routes, for example to add custom validation, see [models/00_urls.py](models/00_urls.py). You are also free to set any types of routes that you need for the model and the `json_schema` and `db_schema` properties are not required in this case. You may for example have a model that uses a different database or no database at all, see [models/articles.py](models/articles.py). The `routes` property needs to be a list of dictionaries with the keys `method`, `path`, `handler`, and the optional keys `name` (name of the route, defaults to the name of handler function), `request_schema` (JSON schema to validate in request body), `response_schema` (JSON schema of response body), and `parameters` (a list of [OpenAPI parameters](https://swagger.io/docs/specification/describing-parameters/) to validate in path/query/header - see [models/articles.py](models/articles.py)). The default CRUD routes are defined in [model_routes.py](content_api/model_routes.py).

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

Models are read in alphabetical filename order and the [urls](models/00_urls.py) model has a PostgreSQL table with a reference to the [fetches](models/01_fetches.py) table which is why the model files have number prefixes in the filename.

Here is a short description of the most important modules in the [content_api](content_api) directory:

* [model_routes](content_api/model_routes.py) - if a model doesn't define a `routes` attribute then the CRUD routes in `model_routes` is used. Model routes are at the heart of the content API since they define the routing for the web framework (i.e. Flask), are used to generate the OpenAPI documentation, and are used as the basis for request validation (with JSON schema).
* [model_api](content_api/model_api.py) - has the default CRUD handlers used by `model_routes` and talks to a database module like [db/pg](content_api/db/pg.py).
* [models](content_api/models.py) - reads all the models in the `models` directory and sets some defaults for those models. Also has a `create_schema` function for creating the PostgreSQL schema (tables) for all models.
* [request_validation](content_api/request_validation.py) - handles JSON schema validation of `query`, `path`, and `header` parameters as well as the request body for `PUT` and `POST` requests. Uses the `model_routes` as input.
* [swagger](content_api/swagger.py) - creates the OpenAPI `sagger.json` specification based on the `model_routes`.
* [json_schema](content_api/json_schema.py) - handles JSON schema validation and type coercion based on JSON schema types. Type coercion is needed since query, path, and header parameters come in as strings and for the request body since JSON doesn't have a datetime type
* [app_test](content_api/app_test.py) - end-to-end HTTP level testing of the model API, primarily for the CRUD operations of the `urls` example model, validation, sorting, filtering, pagination etc.
* [db/pg](content_api/db/pg.py) - the PostgreSQL database interface
* [db/mongodb](content_api/db/mongodb.py) - the MongoDB database interface

## OpenAPI and JSON Schema

As of version 3.1 OpenAPI has full [JSON Schema](http://json-schema.org/understanding-json-schema/) support but versions prior to 3.1, [did not](https://swagger.io/docs/specification/data-models/keywords/). Examples of unsupported features were `patternProperties` and `type` properties with array (multiple) values, i.e. specifying that a value can be either a `string` or a `number` etc.

To add additional capabilities to your schemas you can use [OpenAPI extension properties](https://swagger.io/docs/specification/openapi-extensions). One approach that I have used it to put all my extensions under a single `x-meta` property where I put all the metadata that I need.

## Decorators

What's usually referred to as `middleware` in web frameworks can be achieved
by adding [Python decorators](https://www.programiz.com/python-programming/decorator) to
a route `handler`, see for example how this is done in [model_api.py](content_api/model_api.py) and
in [content_api/models.py](content_api/models.py) or in this simple example model (notice that the order of decorators potentially matters):

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

Composing decorators is straight forward, see [models/composed_decorators_example.py](models/composed_decorators_example.py).


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
BASE_URL=https://python-rest-api-112f9b8f7887.herokuapp.com venv/bin/pytest -s -vv content_api/app_test.py
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

## Talking to Postgres

From python:

```sh
python
import content_api.db.pg as db
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
import content_api.db.mongodb as db
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

## Deployment with Heroku

Specify Python version and Procfile for Heroku:

```sh
python --version # => Python 3.11.6
echo 'python-3.11.6' > runtime.txt
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
heroku addons:create heroku-postgresql:mini
```

Create the model schemas:

```sh
heroku run python -c "import content_api.models as models; models.create_schema()"
```

Run the tests:

```sh
BASE_URL=https://python-rest-api-112f9b8f7887.herokuapp.com venv/bin/pytest -s -vv content_api/app_test.py
```

Check out the OpenAPI docs:

```sh
heroku open
```

The API tests can be run against the deployed app like so:

```sh
BASE_URL=<heroku-url> python -m pytest -s app_test.py
```

## Resources

* [Understanding JSON Schema](http://json-schema.org/understanding-json-schema/)
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
* [Heroku Python Getting Started App](https://github.com/heroku/python-getting-started)