from model_api import make_model_api
import models.urls

MODELS = [
    models.urls
]

id_parameter = {
    'name': 'id',
    'in': 'path',
    'required': True,
    'schema': {
        'type': 'integer'
    }
}

def request_body(model):
    return {
        'content': {
            'application/json': {
                'schema': model.json_schema
            }
        }
    }

def get_model_routes(models = MODELS):
    routes = []
    for model in models:
        model_api = make_model_api(model.name, model.json_schema)
        list_path = f'/v1/{model.name}'
        get_path = f'/v1/{model.name}/<id>'
        routes = routes + [
            {
                'method': 'GET',
                'path': list_path,
                'handler': model_api.list,
                'model': model
            },
            {
                'method': 'GET',
                'path': get_path,
                'handler': model_api.get,
                'model': model,
                'parameters': [
                    id_parameter
                ]
            },
            {
                'method': 'POST',
                'path': list_path,
                'handler': model_api.create,
                'model': model,
                'requestBody': request_body(model)
            },
            {
                'method': 'PUT',
                'path': get_path,
                'handler': model_api.update,
                'model': model,
                'parameters': [
                    id_parameter,
                ],
                'requestBody': request_body(model)
            },
            {
                'method': 'DELETE',
                'path': get_path,
                'handler': model_api.delete,
                'model': model,
                'parameters': [
                    id_parameter
                ]
            }
        ]
    return routes
