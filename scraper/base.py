from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional
from urllib.parse import urljoin

from playwright.sync_api import sync_playwright, Page, Browser, ElementHandle

from scraper.models.models import Category, Product, ProductAttribute


class BaseScraper(ABC):
    def __init__(self, base_url: str, headless: bool = True, output_path: Optional[Path] = None):
        self.base_url = base_url
        self.headless = headless
        self.output_path = output_path  # Store where to save
        self.playwright = None
        self.browser = None
        self.root_node = None

    def _setup(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=self.headless)

    def _teardown(self):
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

    def scrape(self) -> Category:
        """
        Main entry point for scraping.
        """
        self._setup()
        try:
            return self._scrape_impl()
        finally:
            self._teardown()

    def save_checkpoint(self):
        """Saves the current state of root_node to disk."""
        if self.output_path and self.root_node:
            self.output_path.write_text(self.root_node.model_dump_json(indent=2))
            print(f"Saved checkpoint to: {self.output_path}")

    @staticmethod
    def _get_attr(el: ElementHandle, selector: str, attr: str) -> Optional[str]:
        """
        Reads attribute from a child matched by `selector` relative to `el`.
        Use ':scope' to read attribute from `el` itself.
        """
        if selector == ":scope":
            return el.get_attribute(attr)

        child = el.query_selector(selector)
        return child.get_attribute(attr) if child else None

    @staticmethod
    def _get_text(el: ElementHandle, selector: str) -> str:
        """Reads inner_text from a child matched by `selector` relative to `el`."""
        child = el.query_selector(selector)
        return child.inner_text().strip() if child else ""

    @staticmethod
    def _process_url(base_url: str, page_url: str, raw: str | None) -> str | None:
        """
        Normalize href/src values into absolute URLs.
        """
        if not raw:
            return raw

        raw = (raw or "").strip()
        if not raw:
            return ""

        if raw.startswith(("http://", "https://")):
            return raw

        # Prefer configured base_url, fallback to current page
        return urljoin(base_url or page_url, raw)

    @abstractmethod
    def _scrape_impl(self) -> Category:
        """
        Implementation of the scraping logic.
        """
        pass

    @abstractmethod
    def get_categories(self, page: Page) -> List[Category]:
        pass

    @abstractmethod
    def get_products(self, page: Page) -> List[Product]:
        pass

    @abstractmethod
    def enrich_product(self, product: Product) -> Product:
        pass

    @abstractmethod
    def get_product_attributes(self, page: Page) -> List[ProductAttribute]:
        pass
