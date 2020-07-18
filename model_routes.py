from json_schema import writable_schema

id_parameter = {
    'name': 'id',
    'in': 'path',
    'required': True,
    'schema': {
        'type': 'integer'
    }
}

default_route_names = ['list', 'get', 'create', 'update', 'delete']

def get_model_routes(name, json_schema, api, route_names = default_route_names):
    write_schema = writable_schema(json_schema)
    list_path = f'/v1/{name}'
    get_path = f'/v1/{name}/<id>'
    all_routes = [
        {
            'method': 'GET',
            'path': list_path,
            'handler': api.list,
            'model_name': name,
            'response_schema': api.response_schema('list')
        },
        {
            'method': 'GET',
            'path': get_path,
            'handler': api.get,
            'model_name': name,
            'parameters': [
                id_parameter
            ],
            'response_schema': api.response_schema('get')
        },
        {
            'method': 'POST',
            'path': list_path,
            'handler': api.create,
            'model_name': name,
            'request_schema': write_schema,
            'response_schema': api.response_schema('create')
        },
        {
            'method': 'PUT',
            'path': get_path,
            'handler': api.update,
            'model_name': name,
            'parameters': [
                id_parameter,
            ],
            'request_schema': write_schema,
            'response_schema': api.response_schema('update')
        },
        {
            'method': 'DELETE',
            'path': get_path,
            'handler': api.delete,
            'model_name': name,
            'parameters': [
                id_parameter
            ],
            'response_schema': api.response_schema('delete')
        }
    ]
    return [r for r in all_routes if r['handler'].__name__ in route_names]
