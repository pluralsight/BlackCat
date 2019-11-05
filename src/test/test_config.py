from util.config import Config


def test_config():
    c = Config(filename='test_config.yml')
    assert c.github.access_token == ''
    assert c.github.org_names[0] == 'octocat'
