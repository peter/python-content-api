# Example Python Heroku CRUD API

Features:

* Postgresql access with psycopg2
* Generic CRUD model API that is easy to adapt to Flask or serverless etc.
* Flask CRUD API (a thin wrapper around the model API)
* Validation with jsonschema
* API testing with pytest and the request package
* OpenAPI/Swagger documentation generated from model routes

## Setting up Development Environment

Install packages in a virtual env:

```sh
python -m venv venv
. venv/bin/activate
pip install -r requirements.txt
```

Create database:

```sh
createdb -U postgres python-heroku-kitchensink
python -c "import db; db.create_schema()"
```

Start server:

```sh
bin/start-dev

open http://localhost:5000
```

## Running the API tests

```sh
bin/test
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

```
export BASE_URL=http://localhost:5000

# create with invalid data yields 400
curl -i -H "Content-Type: application/json" -X POST -d '{"url":"http://www.google.com", "foo": 1}' $BASE_URL/v1/urls

# successful create
curl -i -H "Content-Type: application/json" -X POST -d '{"url":"http://www.google.com"}' $BASE_URL/v1/urls

# list
curl -i $BASE_URL/v1/urls

# get of non-existant id yields 404
curl -i $BASE_URL/v1/urls/2

# get
curl -i $BASE_URL/v1/urls/1

# update of non-existant id yields 404
curl -i -H "Content-Type: application/json" -X PUT -d '{"url":"http://www.yahoo.com"}' $BASE_URL/v1/urls/2

# update with invalid data yields 400
curl -i -H "Content-Type: application/json" -X PUT -d '{"url":"http://www.yahoo.com", "foo": 1}' $BASE_URL/v1/urls/1

# successful update
curl -i -H "Content-Type: application/json" -X PUT -d '{"url":"http://www.yahoo.com"}' $BASE_URL/v1/urls/1

# Check the update happened
curl -i $BASE_URL/v1/urls
curl -i $BASE_URL/v1/urls/1

# delete of non-existant id yields 404
curl -i -X DELETE $BASE_URL/v1/urls/2

# successful delete
curl -i -X DELETE $BASE_URL/v1/urls/1

# Check the delete happened
curl -i $BASE_URL/v1/urls
curl -i $BASE_URL/v1/urls/1
```

## Talking to Postgres

From python:

```sh
python
import db
from datetime import datetime

# list
db.query("select * from urls")

# create
db.execute('INSERT INTO urls (url, created_at) VALUES (%s, %s)', ("http://www.aftonbladet.se", datetime.now()))

# get
db.query_one("select * from urls where id = %s", [1])

# update
db.execute('UPDATE urls SET url = %s where id = %s', ("http://www.expressen.se", 1))

# delete
db.execute('DELETE from urls where id = %s', [1])
```

Connecting with psql:

```
psql -U postgres python-heroku-kitchensink
```

## How this app was created

Create and activate virtual python env for this project:

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

Created script `bin/start-dev` and basic `app.py`.

Push files to git:

```sh
git add .
git commit -m 'hello world'
git push heroku master
```

Test the app:

```sh
heroku open
```

## Deployment with Heroku

Specified Python version and Procfile for Heroku:

```sh
python --version # => Python 3.7.7
echo 'python-3.7.7' > runtime.txt
echo 'web gunicorn app:app' > Procfile
```

Create heroku app:

```sh
heroku apps:create --region eu python-heroku-kitchensink
```


Deploy:

```sh
git push heroku master
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

The `zappa init` command will create a `zappa_settings.json` file like this:

```json
{
    "production": {
        "app_function": "app.app",
        "profile_name": "private",
        "aws_region": "eu-north-1",
        "project_name": "python-heroku-k",
        "runtime": "python3.8",
        "s3_bucket": "zappa-python-heroku-kitchensink"
    }
}
```

Deploy:

```sh
zappa deploy production
```

Zappa error: [Status check on the deployed lambda failed](https://github.com/Miserlou/Zappa/issues/1985), see also [Error loading psycopg2 module](https://github.com/Miserlou/Zappa/issues/800).

Zappa debug logs:

```sh
zappa tail
```

Used the AWS console for lambda to set the DATABASE_URL [env variable](https://github.com/Miserlou/Zappa#setting-environment-variables) for the Heroku app.

Issue: the AWS lambda app is deployed at a URL like `https://ivjv8xpkkj.execute-api.eu-north-1.amazonaws.com/production` i.e. it is not deployed at the root path `/` but rather at `/production`. This breaks the swagger UI.

The API tests can be run against the deployed app like so:

```sh
BASE_URL=https://ivjv8xpkkj.execute-api.eu-north-1.amazonaws.com/production python -m pytest -s app_test.py
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

Serverless (AWS Lambda) deployment:

* [Chalice - Serverless Python](https://realpython.com/aws-chalice-serverless-python/)
* [AWS Lambda with Python - Simple Example](https://www.scalyr.com/blog/aws-lambda-with-python/)
* [AWS Lambda with Python - Getting Started Guide](https://stackify.com/aws-lambda-with-python-a-complete-getting-started-guide/)
* [The Official Guide to Serverless Flask](https://www.serverless.com/flask)
