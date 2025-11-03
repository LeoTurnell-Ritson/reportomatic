import configparser
import os
from abc import ABC, abstractmethod
from urllib.parse import urlparse

from .states import IssueState, MilestoneState, PullState


class Adapter(ABC):

    def __init__(self, url):
        parsed = urlparse(url)
        self._url = url
        self._scheme = parsed.scheme
        self._hostname = parsed.hostname
        self._path = parsed.path.strip("/")
        self._connection = self.connection

    @property
    def _token(self):
        conf_path = os.path.expanduser("~/.reportomatic.conf")
        config = configparser.ConfigParser()
        if not os.path.exists(conf_path):
            raise FileNotFoundError(f"Config file not found: {conf_path}")

        config.read(conf_path)
        if "auth" not in config:
            raise KeyError("Missing 'auth' section in config file")

        token = config["auth"].get(self._hostname)
        if not token:
            raise KeyError(f"Missing token for host: {self._hostname}")

        return token.strip()

    @property
    def path(self):
        return self._path

    @property
    @abstractmethod
    def connection(self):
        pass

    @property
    @abstractmethod
    def project(self):
        pass

    @abstractmethod
    def issues(self, state=IssueState.OPEN, updated_after=None):
        pass

    @abstractmethod
    def pulls(self, state=PullState.OPEN, updated_after=None):
        pass

    @abstractmethod
    def milestones(self, state=MilestoneState.OPEN, updated_after=None):
        pass
