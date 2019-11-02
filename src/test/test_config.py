from util.config import Config


def test_config():
    c = Config(filename='../../config.example.yml')
    assert c.github.access_token == ''
    assert c.github.org_name == 'octocat'
