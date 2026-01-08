from abc import ABC, abstractmethod
from typing import List

from playwright.sync_api import Page

from scraper.models.models import ProductFile


class ProductFileExtractor(ABC):

    @staticmethod
    def _infer_type(filename: str) -> str | None:
        filename = filename.lower()
        for ext in (".pdf", ".jpg", ".jpeg", ".png", ".doc", ".docx"):
            if filename.endswith(ext):
                return ext.lstrip(".")
        return None

    @abstractmethod
    def extract(self, page: Page) -> List[ProductFile]:
        pass
