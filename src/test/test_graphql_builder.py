from src.github.graphql_call import dict_to_query, GraphQLCall
from unittest.mock import Mock, patch


def test_dict_to_query():
    out = dict_to_query({'a': 'b', 'c': 1})
    assert out == 'a:"b",c:1'

    out = dict_to_query({})
    assert out == ''

    # noinspection PyTypeChecker
    out = dict_to_query(None)
    assert out == ''

def test_grapqhl_query():
    call = GraphQLCall('query {{ viewer {{ {viewer} }} }}')
    with patch('src.github.graphql_call.requests.post') as p:
        p.return_value.ok = True
        p.return_value.json = lambda: {'test': 'test'}
        resp = call.call('dummy', {'viewer': 'test'})
        assert resp.ok
        assert resp.json() == {'test': 'test'}
