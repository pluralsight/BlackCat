import logging
import os
from abc import ABC, abstractmethod
from typing import Optional

import yaml

from blackcat.util.splunk_hec_handler import SplunkHecHandler


class Config(object):
    def __init__(self, filename: Optional[str] = 'config.yml'):
        with open(filename) as f:
            self.data = yaml.safe_load(f).get('black_cat')
            self.github = GitHubConfig(self.data.get('github'))
            self.logging = LoggingConfig(self.data.get('logging'))


class GitHubConfig(object):
    def __init__(self, config: dict):
        env_names = os.getenv('ORG_NAMES', None)
        self.org_names = env_names.split(',') if env_names else config.get('org_names')
        # Get from environment variable or config
        self.access_token = os.getenv('GIT_TOKEN', config.get('access_token'))


class LoggingConfig(object):
    def __init__(self, config: dict):
        self.splunk = config.get('splunk')
        if self.splunk and self.splunk.get('enabled'):
            self.logger = logging.getLogger('splunk')
            self.logger.setLevel(logging.INFO)
            SplunkLoggingBackend(self.splunk).apply_handler(self.logger)
        else:
            self.logger = None


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
                                proto=self.proto, sourcetype=self.source_type, ssl_verify=True, index=self.index)

    def __init__(self, config: dict):
        super().__init__(config)
        self.domain = os.getenv('SPLUNK_DOMAIN', config.get('domain'))
        self.port = os.getenv('SPLUNK_PORT', config.get('port'))
        self.proto = config.get('proto')
        self.source_type = config.get('source_type', 'blackcat')
        self.index = config.get('index')

        # Get from environment variable or config
        self.hec_token = os.getenv('SPLUNK_HEC', config.get('hec_token'))
