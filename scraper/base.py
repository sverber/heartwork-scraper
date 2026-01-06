from abc import ABC, abstractmethod
from typing import List, Optional
from playwright.sync_api import sync_playwright, Page, Browser
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
