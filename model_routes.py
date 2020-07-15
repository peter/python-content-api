import models.urls
import models.fetches
from json_schema import writable_schema

MODELS = [
    models.urls,
    models.fetches
]

id_parameter = {
    'name': 'id',
    'in': 'path',
    'required': True,
    'schema': {
        'type': 'integer'
    }
}

def get_model_routes(models = MODELS):
    routes = []
    for model in models:
        write_schema = writable_schema(model.json_schema)
        list_path = f'/v1/{model.name}'
        get_path = f'/v1/{model.name}/<id>'
        routes = routes + [
            {
                'method': 'GET',
                'path': list_path,
                'handler': model.api.list,
                'model': model,
                'response_schema': model.api.response_schema('list')
            },
            {
                'method': 'GET',
                'path': get_path,
                'handler': model.api.get,
                'model': model,
                'parameters': [
                    id_parameter
                ],
                'response_schema': model.api.response_schema('get')
            },
            {
                'method': 'POST',
                'path': list_path,
                'handler': model.api.create,
                'model': model,
                'request_schema': write_schema,
                'response_schema': model.api.response_schema('create')
            },
            {
                'method': 'PUT',
                'path': get_path,
                'handler': model.api.update,
                'model': model,
                'parameters': [
                    id_parameter,
                ],
                'request_schema': write_schema,
                'response_schema': model.api.response_schema('update')
            },
            {
                'method': 'DELETE',
                'path': get_path,
                'handler': model.api.delete,
                'model': model,
                'parameters': [
                    id_parameter
                ],
                'response_schema': model.api.response_schema('delete')
            }
        ]
    return routes
