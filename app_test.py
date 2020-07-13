import os
import requests
import uuid
import app
from util import get

BASE_URL = os.getenv('BASE_URL', 'http://localhost:5001')

def uuid_hex():
    return uuid.uuid4().hex

def first(the_iterable, condition = lambda x: True):
    for i in the_iterable:
        if condition(i):
            return i

def test_crud():
  list_url = f'{BASE_URL}/v1/urls'
  doc = {'url': f'http://{uuid_hex()}.example.com'}

  # Create with invalid schema
  invalid_doc = {**doc, 'foo': 1}
  response = requests.post(list_url, json=invalid_doc)
  assert response.status_code == 400
  assert get(response.json(), 'error.message')

  # Successful create
  response = requests.post(list_url, json=doc)
  assert response.status_code == 200
  assert response.json()['url'] == doc['url']
  assert response.json()['id']
  assert response.json()['created_at']
  doc['id'] = response.json()['id']

  get_url = f'{list_url}/{doc["id"]}'

  # Verify create with get
  response = requests.get(get_url)
  assert response.status_code == 200
  assert response.json()['id'] == doc['id']
  assert response.json()['url'] == doc['url']

  # Get 404
  get_url_404 = f'{list_url}/{doc["id"] + 100}'
  response = requests.get(get_url_404)
  assert response.status_code == 404

  # Get invalid id
  response = requests.get(f'{list_url}/fooobar')
  assert response.status_code == 400
  assert get(response.json(), 'error.message')

  # Create with url that already exists
  response = requests.post(list_url, json={'url': doc['url']})
  print(response.json())
  assert response.status_code == 400
  assert get(response.json(), 'error.message')

  # List
  response = requests.get(list_url)
  assert response.status_code == 200
  list_doc = first(response.json(), lambda d: d['id'] == doc['id'])
  assert list_doc['url'] == doc['url']

  new_url = f'http://{uuid_hex()}.example.com'

  # Update 404
  response = requests.put(get_url_404, json={'url': new_url})
  assert response.status_code == 404

  # Update with invalid schema
  response = requests.put(get_url, json={'url': 123})
  assert response.status_code == 400
  assert get(response.json(), 'error.message')

  # Successful update
  response = requests.put(get_url, json={'url': new_url})
  assert response.status_code == 200

  # Verify update
  response = requests.get(get_url)
  assert response.status_code == 200
  assert response.json()['url'] == new_url

  # Delete 404
  response = requests.delete(get_url_404)
  assert response.status_code == 404

  # Successful delete
  response = requests.delete(get_url)
  assert response.status_code == 200

  # Verify delete
  response = requests.get(get_url)
  assert response.status_code == 404
