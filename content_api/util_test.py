from content_api.util import get

# See: https://stackoverflow.com/questions/4014621/a-python-class-that-acts-like-dict
class DictLike:
    def __init__(self, **dict):
      self.__dict__ = dict
    def __getitem__(self, key):
        return self.__dict__[key]
    def __contains__(self, item):
        return item in self.__dict__

class NotDictLike:
    def __init__(self, **dict):
      self.__dict__ = dict
    def __getitem__(self, key):
        return self.__dict__[key]

def test_get():
    assert get(None, ['foo']) == None
    assert get({'foo': 1}, None) == None
    assert get(None, None) == None
    assert get({'foo': 1}, []) == {'foo': 1}
    assert get({'foo': 1}, ['foo']) == 1
    assert get({'foo': 1}, ['bar']) == None
    assert get({'foo': 1}, ['bar'], 'the default') == 'the default'
    assert get({'foo': {'bar': 'hello'}}, ['foo', 'bar']) == 'hello'
    assert get({'foo': {'bar': 'hello'}}, 'foo.bar') == 'hello'
    assert get(DictLike(**{'foo': {'bar': 'hello'}}), 'foo.bar') == 'hello'
    assert get(NotDictLike(**{'foo': {'bar': 'hello'}}), 'foo.bar') == None
    assert get({'foo': [{'bar': 'hello'}]}, 'foo.0.bar') == 'hello'
    assert get({'foo': [{'bar': 'hello'}]}, 'foo.1') == None
    assert get({'foo': [{'bar': 'hello'}]}, 'foo.1.bar') == None
    assert get(['foo', 'bar'], '1') == 'bar'
    assert get(['foo', 'bar'], '2') == None
