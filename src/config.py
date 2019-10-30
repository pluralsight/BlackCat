import logging
from abc import ABC, abstractmethod
from typing import Optional

import yaml

from src.splunk_hec_handler import SplunkHecHandler


class Config(object):
    def __init__(self, filename: Optional[str] = 'config.yml'):
        with open(filename) as f:
            self.data = yaml.safe_load(f).get('black_cat')
            self.github = GitHubConfig(self.data.get('github'))
            self.logging = LoggingConfig(self.data.get('logging'))


class GitHubConfig(object):
    def __init__(self, config: dict):
        self.org_name = config.get('org_name')
        self.access_token = config.get('access_token')


class LoggingConfig(object):
    def __init__(self, config: dict):
        self.splunk = config.get('splunk')
        if self.splunk and self.splunk.get('enabled'):
            self.logger = logging.getLogger('splunk')
            self.logger.setLevel(logging.INFO)
            SplunkLoggingBackend(self.splunk).apply_handler(self.logger)


class LoggingBackend(ABC):
    def __init__(self, config: dict):
        self.enabled = config.get('enabled')

    @abstractmethod
    def get_handler(self):
        pass

    def apply_handler(self, logger):
        logger.addHandler(self.get_handler())


class SplunkLoggingBackend(LoggingBackend):
    def get_handler(self):
        return SplunkHecHandler(host=self.domain, token=self.hec_token, port=self.port,
                                proto=self.proto, source=self.source_type, ssl_verify=True, index=self.index)

    def __init__(self, config: dict):
        super().__init__(config)
        self.domain = config.get('domain')
        self.port = config.get('port')
        self.proto = config.get('proto')
        self.source_type = config.get('source_type')
        self.index = config.get('index')
        self.hec_token = config.get('hec_token')
