# Example Python Heroku App

## Setting up Development Environment

```sh
python -m venv env
pip install -r requirements.txt

createdb python_heroku_starter

bin/start-dev

open http://localhost:5000
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

## Resources

* [Python Flask/Auth/Heroku Example app](https://github.com/peter/api-auth-examples/tree/master/flask)

* [Getting Started on Heroku with Python](https://devcenter.heroku.com/articles/getting-started-with-python?singlepage=true)
* [Deploying Python Applications with Gunicorn (Heroku)](https://devcenter.heroku.com/articles/python-gunicorn)
* [Gunicorn homepage](https://gunicorn.org)
* [Specifying a Python Runtime](https://devcenter.heroku.com/articles/python-runtimes)
* [Most Popular Python Packages](https://pypistats.org/top)
