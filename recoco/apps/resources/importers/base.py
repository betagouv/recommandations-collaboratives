from abc import ABC, abstractmethod
from urllib.parse import urlparse

import requests


class BaseRIAdapter(ABC):
    """Interface for external Resource adapters such as MediaWiki"""

    def __init__(self, uri):
        self.uri = uri
        self.parsed_uri = urlparse(uri)
        self.raw_data = None

        # Mirror fields of `Resource`
        self.title = None
        self.content = None

    @staticmethod
    @abstractmethod
    def can_handle(response: requests.Response) -> bool:
        return NotImplemented

    @abstractmethod
    def load_data(self, response: requests.Response) -> bool:
        return NotImplemented

    @abstractmethod
    def extract_data(self) -> None:
        return NotImplemented
