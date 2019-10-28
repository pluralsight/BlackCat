import json
import logging
import re
import time
from typing import Optional

from pip._vendor import requests

from src.github.exception import InvalidQueryException

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

    def call(self, token: str, **kwargs: Optional[dict]):
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
        resp = requests.post(url=self.ENDPOINT, headers={'Authorization': 'Bearer {}'.format(token)}, json={'query': data})
        # ratelimit = resp.headers.get('X-RateLimit-Remaining')
        return resp

    def pages(self, token: str, cursor_var_name: str, **kwargs: Optional[dict]):
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
            # Ratelimit logic
            remaining_ratelimit = int(resp.headers.get('X-RateLimit-Remaining'))
            reset_time = int(resp.headers.get('X-Ratelimit-Reset'))

            if remaining_ratelimit <= 400:
                time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(reset_time))
                logging.info('Sleeping until ratelimit reset ({})...'.format(time_str))
                time_delta = reset_time - time.time()
                while time.time() < reset_time:
                    logging.info('Timer will reset in {} seconds ({}). Sleeping for 300s...'.format(time_delta, time_str))
                    time.sleep(300)

            # Next page
            if not resp.json().get('data') or not resp.json().get('data').get('organization'):
                raise InvalidQueryException(json.dumps(resp.json().get('errors')))
            out.append(resp.json())
            page_info = resp.json().get('data').get('organization').get('repositories').get('pageInfo')
            cursor = page_info.get('endCursor')

        return out




