from typing import Optional

import yaml


class Config(object):
    def __init__(self, filename: Optional[str] = 'config.yml'):
        with open(filename) as f:
            self.dict = yaml.safe_load(f).get('black_cat')
            self.github = GitHubConfig(self.dict.get('github'))

class GitHubConfig(object):
    def __init__(self, config: dict):
        self.org_name = config.get('org_name')
        self.access_token = config.get('access_token')