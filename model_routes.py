from db import db
from model_api import filter_param_pattern

id_parameter = {
    'name': 'id',
    'in': 'path',
    'required': True,
    'schema': db.id_json_schema
}

def list_parameters(json_schema):
    return [
        {
            'name': 'limit',
            'in': 'query',
            'required': False,
            'schema': {'type': 'integer', 'minimum': 1, 'maximum': 100}
        },
        {
            'name': 'offset',
            'in': 'query',
            'required': False,
            'schema': {'type': 'integer', 'minimum': 0}
        },
        {
            'name': 'sort',
            'in': 'query',
            'required': False,
            'schema': {'type': 'string'},
            'description': 'Sort order on the format column1,column2,column3... For descending sort, use -column1'
        },
        {
            'name': 'filter',
            'in': 'query',
            'required': False,
            'x-meta': {
                'namePattern': filter_param_pattern(json_schema)
            },
            'schema': {'type': 'string'},
            'description': 'Filters to query by, i.e. filter.column=foobar (equals), filter.column[contains]=foobar (contains/includes), filter.created_at[lt]=2020-08-06%2009:31:28.092946 (less than), filter.created_at[lt]=2020-08-06%2009:31:28.092946 (greater than)'
        }
    ]

default_route_names = ['list', 'get', 'create', 'update', 'delete']

def get_model_routes(name, json_schema, api, route_names = default_route_names):
    list_path = f'/v1/{name}'
    get_path = f'/v1/{name}/<id>'
    all_routes = [
        {
            'method': 'GET',
            'path': list_path,
            'name': 'list',
            'handler': api.list,
            'model_name': name,
            'parameters': list_parameters(json_schema),
            'response_schema': api.response_schema('list')
        },
        {
            'method': 'GET',
            'path': get_path,
            'name': 'get',
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
            'name': 'create',
            'handler': api.create,
            'model_name': name,
            'request_schema': json_schema,
            'response_schema': api.response_schema('create')
        },
        {
            'method': 'PUT',
            'path': get_path,
            'name': 'update',
            'handler': api.update,
            'model_name': name,
            'parameters': [
                id_parameter,
            ],
            'request_schema': json_schema,
            'response_schema': api.response_schema('update')
        },
        {
            'method': 'DELETE',
            'path': get_path,
            'name': 'delete',
            'handler': api.delete,
            'model_name': name,
            'parameters': [
                id_parameter
            ],
            'response_schema': api.response_schema('delete')
        }
    ]
    return [r for r in all_routes if r['name'] in route_names]
