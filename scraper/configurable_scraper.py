from typing import List, Set
from urllib.parse import urljoin, urlparse

from playwright.sync_api import Page

from scraper.base import BaseScraper
from scraper.config import ScraperConfig
from scraper.models import Category, Product


class ConfigurableScraper(BaseScraper):
    def __init__(self, base_url: str, config: ScraperConfig, headless: bool = True):
        super().__init__(base_url, headless)
        self.config = config

    def _resolve_url(self, page_url: str, href: str) -> str:
        # Resolve relative URLs
        full_url = href if href.startswith("http") else f"{self.base_url.rstrip('/')}/{href.lstrip('/')}"

        # A robust urljoin is better:
        full_url = urljoin(page_url, href)

        # Fix common URL issues: duplicate adjacent segments
        # e.g. /onze-collecties/onze-collecties/ -> /onze-collecties/
        parsed = urlparse(full_url)
        path_segments = [s for s in parsed.path.split('/') if s]

        new_segments = []
        if path_segments:
            new_segments.append(path_segments[0])
            for i in range(1, len(path_segments)):
                if path_segments[i] != path_segments[i - 1]:
                    new_segments.append(path_segments[i])

        # Reconstruct path
        new_path = "/" + "/".join(new_segments)
        # Preserve trailing slash if original had it
        if parsed.path.endswith('/') and not new_path.endswith('/'):
            new_path += "/"

        return parsed._replace(path=new_path).geturl()

    def _scrape_impl(self) -> Category:
        self.visited_urls: Set[str] = set()
        page = self.browser.new_page()
        page.goto(self.base_url)

        root = Category(name="Root", url=self.base_url)
        self._traverse(page, root)
        return root

    def _traverse(self, page: Page, current_category: Category):
        curr_url = str(current_category.url).rstrip('/')
        self.visited_urls.add(curr_url)
        print(f"Traversing: {current_category.url}")

        # 1. Get Subcategories
        subcategories = self.get_categories(page)
        current_category.subcategories = subcategories

        # 2. Get Products
        products = self.get_products(page)
        current_category.products = products

        # 3. Recurse into subcategories
        # Note: traversing *all* subcategories can be very slow. 
        # For a real implementation, you might want to manage this queue differently.
        # But for this task, we will visit them.
        for subcat in subcategories:
            # We need to navigate to the subcat URL. 
            # Ideally we open a new page or re-use. Re-using is simpler but requires back navigation or reloading.
            # Let's use a new page context or just navigate.
            # Navigation is safer to specific URL.
            sub_url = str(subcat.url).rstrip('/')
            if sub_url in self.visited_urls:
                continue

            try:
                sub_page = self.browser.new_page()
                sub_page.goto(str(subcat.url))
                self._traverse(sub_page, subcat)
                sub_page.close()
            except Exception as e:
                print(f"Failed to traverse {subcat.url}: {e}")

    def get_categories(self, page: Page) -> List[Category]:
        categories = []
        # Use the config selector
        elements = page.query_selector_all(self.config.category_selector)
        for el in elements:
            href = el.get_attribute("href")
            name = el.inner_text().strip()
            if href:
                full_url = self._resolve_url(page.url, href)
                categories.append(Category(name=name, url=full_url))
        return categories

    def get_products(self, page: Page) -> List[Product]:
        products = []
        elements = page.query_selector_all(self.config.product_selector)
        for el in elements:
            href = el.get_attribute("href")
            name = el.inner_text().strip()
            if href:
                full_url = self._resolve_url(page.url, href)
                products.append(Product(name=name, url=full_url))
        return products
