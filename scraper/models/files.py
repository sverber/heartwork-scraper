from abc import ABC, abstractmethod
from typing import List

from playwright.sync_api import Page

from scraper.models.models import ProductFile


class ProductFileExtractor(ABC):
    @abstractmethod
    def extract(self, page: Page) -> List[ProductFile]:
        pass
