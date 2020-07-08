# Example Python Heroku App

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

Connecting to postgres:

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

Specify Python version and Procfile for Heroku:

```sh
python --version # => Python 3.7.7
echo 'python-3.7.7' > runtime.txt
echo 'web gunicorn app:app' > Procfile
```

Push files to git:

```sh
git add .
git commit -m 'hello world'
git push heroku master
```

Create heroku app and deploy:

```sh
heroku apps:create --region eu python-heroku-kitchensink
git push heroku master
```

Test the app:

```sh
heroku open
```

## Resources

* [Installing Postgres via Brew on Mac](https://gist.github.com/ibraheem4/ce5ccd3e4d7a65589ce84f2a3b7c23a3)

* [Python Flask/Auth/Heroku Example app](https://github.com/peter/api-auth-examples/tree/master/flask)

* [Getting Started on Heroku with Python](https://devcenter.heroku.com/articles/getting-started-with-python?singlepage=true)
* [Deploying Python Applications with Gunicorn (Heroku)](https://devcenter.heroku.com/articles/python-gunicorn)
* [Gunicorn homepage](https://gunicorn.org)
* [Specifying a Python Runtime](https://devcenter.heroku.com/articles/python-runtimes)
* [Most Popular Python Packages](https://pypistats.org/top)
