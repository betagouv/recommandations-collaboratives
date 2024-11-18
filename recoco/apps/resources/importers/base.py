from abc import ABC, abstractmethod
from urllib.parse import urlparse


class BaseRIAdapter(ABC):
    """Interface for external Resource adapters such as MediaWiki"""

    def __init__(self, uri):
        self.uri = uri
        self.parsed_uri = urlparse(uri)
        self.raw_data = None

    @staticmethod
    @abstractmethod
    def can_handle(generator):
        return NotImplemented

    @abstractmethod
    def load_data(self):
        return NotImplemented

    @abstractmethod
    def extract_markdown(self):
        return NotImplemented
