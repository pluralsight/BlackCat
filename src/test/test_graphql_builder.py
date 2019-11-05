from unittest.mock import patch

from src.github.graphql_call import dict_to_query, GraphQLCall, RepoVulnerabilityCall


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
        resp = call.call('dummy', viewer='test')
        assert resp.ok
        assert resp.json() == {'test': 'test'}


page_idx = 0


def return_pages(page_one, page_two):
    global page_idx
    page_idx += 1
    if page_idx == 1:
        return page_one
    else:
        return page_two


def test_grapqhl_pages():
    page_one_json = {
        'data': {
            'organization': {
                'repositories': {
                    'pageInfo': {
                        'hasNextPage': True,
                        'endCursor': 'abc'
                    }
                }
            }
        }
    }
    page_two_json = {
        'data': {
            'organization': {
                'repositories': {
                    'pageInfo': {
                        'hasNextPage': False,
                        'endCursor': 'abc'
                    }
                }
            }
        }
    }

    call = GraphQLCall('query {{ viewer {{ {viewer}, {after} }} }}')
    with patch('src.github.graphql_call.requests.post') as p:
        p.return_value.ok = True
        p.return_value.headers = {'X-RateLimit-Remaining': '500', 'X-Ratelimit-Reset': '0'}
        p.return_value.json = lambda: return_pages(page_one_json, page_two_json)
        resp = call.pages('dummy', 'after', viewer='test')
        global page_idx
        page_idx = 0
        assert len(resp) == 2
        assert resp[0] == page_one_json
        assert resp[1] == page_two_json


def test_vuln_query():
    page_one_json = {
        'data': {
            'organization': {
                'repositories': {
                    'edges': [{
                        'url': 'https://github.com/octocat/hello-worId',
                        'securityVulnerability': {
                        }
                    }],
                    'pageInfo': {
                        'hasNextPage': True,
                        'endCursor': 'abc'
                    }
                }
            }
        }
    }
    page_two_json = {
        'data': {
            'organization': {
                'repositories': {
                    'edges': [{
                        'url': 'https://github.com/octocat/hello-worId-two',
                        'securityVulnerability': {
                        }
                    }],
                    'pageInfo': {
                        'hasNextPage': False,
                        'endCursor': 'abc'
                    }
                }
            }
        }
    }

    call = RepoVulnerabilityCall()
    with patch('src.github.graphql_call.requests.post') as p:
        p.return_value.ok = True
        p.return_value.json = lambda: return_pages(page_one_json, page_two_json)
        resp = call.pages('dummy', org_name='test')
        global page_idx
        page_idx = 0
        assert len(resp) == 2
        assert resp[0] == {'url': 'https://github.com/octocat/hello-worId', 'securityVulnerability': {}}
        assert resp[1] == {'url': 'https://github.com/octocat/hello-worId-two', 'securityVulnerability': {}}
