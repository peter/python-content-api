from json_schema import writable_schema

id_parameter = {
    'name': 'id',
    'in': 'path',
    'required': True,
    'schema': {
        'type': 'integer'
    }
}

def get_model_routes(name, json_schema, api):
    write_schema = writable_schema(json_schema)
    list_path = f'/v1/{name}'
    get_path = f'/v1/{name}/<id>'
    return [
        {
            'method': 'GET',
            'path': list_path,
            'handler': api.list,
            'model': name,
            'response_schema': api.response_schema('list')
        },
        {
            'method': 'GET',
            'path': get_path,
            'handler': api.get,
            'model': name,
            'parameters': [
                id_parameter
            ],
            'response_schema': api.response_schema('get')
        },
        {
            'method': 'POST',
            'path': list_path,
            'handler': api.create,
            'model': name,
            'request_schema': write_schema,
            'response_schema': api.response_schema('create')
        },
        {
            'method': 'PUT',
            'path': get_path,
            'handler': api.update,
            'model': name,
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
            'model': name,
            'parameters': [
                id_parameter
            ],
            'response_schema': api.response_schema('delete')
        }
    ]
