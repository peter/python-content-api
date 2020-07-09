import os
import requests
import uuid
import app

BASE_URL = os.getenv('BASE_URL', 'http://localhost:5000')

def uuid_hex():
    return uuid.uuid4().hex

def first(the_iterable, condition = lambda x: True):
    for i in the_iterable:
        if condition(i):
            return i

def test_crud_happy_path():
  list_url = f'{BASE_URL}/v1/urls'
  doc = {'url': f'http://{uuid_hex()}.example.com'}

  response = requests.post(list_url, json=doc)
  assert response.status_code == 200
  assert response.json()['url'] == doc['url']
  assert response.json()['id']
  assert response.json()['created_at']
  doc['id'] = response.json()['id']

  get_url = f'{list_url}/{doc["id"]}'

  response = requests.get(get_url)
  assert response.status_code == 200
  assert response.json()['id'] == doc['id']
  assert response.json()['url'] == doc['url']

  response = requests.get(list_url)
  assert response.status_code == 200
  list_doc = first(response.json(), lambda d: d['id'] == doc['id'])
  assert list_doc['url'] == doc['url']

  new_url = f'http://{uuid_hex()}.example.com'
  response = requests.put(get_url, json={'url': new_url})
  assert response.status_code == 200

  response = requests.get(get_url)
  assert response.status_code == 200
  assert response.json()['url'] == new_url

  response = requests.delete(get_url)
  assert response.status_code == 200

  response = requests.get(get_url)
  assert response.status_code == 404
