from abc import ABC, abstractmethod
from typing import List, Optional
from urllib.parse import urljoin

from playwright.sync_api import sync_playwright, Page, Browser
from playwright.sync_api import sync_playwright, Page, ElementHandle

from scraper.models import Category, Product


class BaseScraper(ABC):
    def __init__(self, base_url: str, headless: bool = True):
        self.base_url = base_url
        self.headless = headless
        self.playwright = None
        self.browser = None

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

    def _get_attr(self, el: ElementHandle, selector: str, attr: str) -> Optional[str]:
        """
        Reads attribute from a child matched by `selector` relative to `el`.
        Use ':scope' to read attribute from `el` itself.
        """
        if selector == ":scope":
            return el.get_attribute(attr)

        child = el.query_selector(selector)
        return child.get_attribute(attr) if child else None

    def _get_text(self, el: ElementHandle, selector: str) -> str:
        """Reads inner_text from a child matched by `selector` relative to `el`."""
        child = el.query_selector(selector)
        return child.inner_text().strip() if child else ""

    def _process_url(self, base_url: str, page_url: str, raw: str) -> str:
        """
        Normalize href/src values into absolute URLs.
        """
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
