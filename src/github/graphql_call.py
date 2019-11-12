import json
import logging
import re
import time

from pip._vendor import requests

from github.exception import InvalidQueryException

VALID_NAME = re.compile('[A-Za-z]+')
REQUEST_FMT = "{}{}{ {} }"


def dict_to_query(val: dict):
    """
    Converts a python dict to graphql query.
    {'a': 'b', 'c': 1}
     becomes
     "a: 'b', b: 1"
    :param val: The dict to use
    :return: The query string
    """
    if not val:
        return ''
    out = []
    for k in val:
        if not val[k]:
            raise InvalidQueryException('Missing value for query parameter {}'.format(k))

        if isinstance(val[k], str):
            val[k] = '"{}"'.format(val[k])
        out.append('{}:{}'.format(k, val[k]))
    return ','.join(out)


def dict_to_fields(val: dict):
    """
    Converts a python dict to graphql fields.
    {'edges': {'node': {'url'}}
     becomes
     a {
    :param val: The dict to use
    :return: The query string
    """
    if not val:
        return ''
    out = []
    for k in val:
        if not val[k]:
            raise InvalidQueryException('Missing value for query parameter {}'.format(k))

        if isinstance(val[k], str):
            val[k] = '"{}"'.format(val[k])
        out.append('{}:{}'.format(k, val[k]))
    return ','.join(out)


class GraphQLCall(object):
    ENDPOINT = 'https://api.github.com/graphql'

    def __init__(self, query_fmt: str):
        self.query = query_fmt

    def call(self, token: str, **kwargs: str):
        """
        Make a paginated request.
        :param token: The token to auth with
        :param kwargs: The arguments to set
        :return: A response
        """
        data = self.query
        if kwargs:
            for k in kwargs:
                if isinstance(kwargs[k], str) and kwargs[k] != 'null':
                    # Wrap strings in quotes
                    # noinspection PyTypeChecker
                    kwargs[k] = '"' + kwargs[k] + '"'

            data = data.format(**kwargs)

        # requests.post({'query': data}, headers={'Authorization', 'bearer {}'.format(token)})
        resp = requests.post(url=self.ENDPOINT, headers={'Authorization': 'Bearer {}'.format(token)},
                             json={'query': data})
        # ratelimit = resp.headers.get('X-RateLimit-Remaining')
        return resp

    def pages(self, token: str, cursor_var_name: str, **kwargs: str):
        """
        Make a paginated request.
        :param token: The token to auth with
        :param cursor_var_name: The variable to replace with the cursor
        :param kwargs: The arguments to set
        :return: An array of page responses
        """
        out = []
        cursor = None
        page_info = None
        while page_info is None or page_info.get('hasNextPage'):
            if cursor is not None:
                kwargs[cursor_var_name] = cursor
            else:
                kwargs[cursor_var_name] = 'null'
            resp = self.call(token, **kwargs)
            # Try one more time if we didn't get a 200.
            retries = 0
            while resp.status_code == 502 and retries < 5:
                logging.info("Recieved unexpected 502. Sleeping for 5 seconds (Retry {}/5)...".format(retries))
                time.sleep(5)
                resp = self.call(token, **kwargs)
                retries += 1

            # Ratelimit logic
            remaining_ratelimit = int(resp.headers.get('X-RateLimit-Remaining', '1000'))
            reset_time = int(resp.headers.get('X-Ratelimit-Reset', '0'))

            if remaining_ratelimit <= 400:
                time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(reset_time))
                logging.info('Sleeping until ratelimit reset ({})...'.format(time_str))
                time_delta = reset_time - time.time()
                while time.time() < reset_time:
                    logging.info(
                        'Timer will reset in {} seconds ({}). Sleeping for 300s...'.format(time_delta, time_str))
                    time.sleep(300)

            # Next page
            json_res = resp.json()
            if not json_res.get('data') or not json_res.get('data').get('organization'):
                raise InvalidQueryException(json.dumps(json_res.get('errors')))
            out.append(json_res)
            page_info = json_res.get('data').get('organization').get('repositories').get('pageInfo')
            cursor = page_info.get('endCursor')

        return out


class RepoVulnerabilityCall(GraphQLCall):
    def pages(self, token: str, **kwargs: str):
        pages = GraphQLCall.pages(self, token, 'after', **kwargs)
        out = []
        for page in pages:
            out += [p for p in page.get('data').get('organization').get('repositories').get('edges')]
        return out

    def __init__(self):
        super().__init__('''{{
                              organization(login: {org_name}) {{
                                repositories(first: 100, isLocked: false, after: {after}) {{
                                  edges {{
                                    node {{
                                      id
                                      url
                                      vulnerabilityAlerts(first: 100) {{
                                        edges {{
                                          node {{
                                            vulnerableManifestPath
                                            dismisser {{
                                              login
                                              name
                                            }}
                                            dismissedAt
                                            dismissReason
                                            securityVulnerability {{
                                              advisory {{
                                                id
                                                identifiers {{
                                                  type
                                                  value
                                                }}
                                                origin
                                                severity
                                                publishedAt
                                                updatedAt
                                                withdrawnAt
                                              }}
                                              package {{
                                                ecosystem
                                                name
                                              }}
                                              firstPatchedVersion {{
                                                identifier
                                              }}
                                              vulnerableVersionRange
                                              severity
                                            }}
                                          }}
                                        }}
                                        pageInfo {{
                                          hasNextPage
                                          endCursor
                                        }}
                                      }}
                                    }}
                                  }}
                                  pageInfo {{
                                    hasNextPage
                                    endCursor
                                  }}
                                }}
                              }}
                            }}'''
                         )
