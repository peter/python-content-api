# Example Python Heroku App

## Setting up Development Environment

```sh
python -m venv env
pip install -r requirements.txt

createdb python_heroku_starter

heroku local
```

## How this app was created

```sh
python --version # => Python 3.7.7
echo 'python-3.7.7' > runtime.txt

python -m venv env
echo 'env' > .gitignore

pip freeze > requirements.txt
```

## Resources

- [Python Flask/Auth/Heroku Example app](https://github.com/peter/api-auth-examples/tree/master/flask)

- [Getting Started on Heroku with Python](https://devcenter.heroku.com/articles/getting-started-with-python?singlepage=true)
- [Specifying a Python Runtime](https://devcenter.heroku.com/articles/python-runtimes)
