from unittest import mock

from blackcat.util.config import Config


def test_config():
    # Will stop splunk from failing to connect
    with mock.patch("socket.socket.connect"):
        c = Config(filename='test/test_config.yml')
    assert c.github.access_token == ''
    assert c.github.org_names[0] == 'octocat'
    assert c.logging is not None
    assert c.logging.logger is not None
