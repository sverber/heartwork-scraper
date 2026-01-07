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

            # Scope check: Verify sub_url belongs to the same site/base path structure
            # This is critical for sites like Yachtpaint where generic links (about, contact, other brands) 
            # might share the same selector class.
            if not sub_url.startswith(self.base_url) and "/products/" not in sub_url:
                # Allow if it's strictly a product filter page we expect, e.g. international-yachtpaint.../products/...
                # But generally we want to stay "under" the base or known paths.
                # For now, let's enforce domain and language match if possible, or just base_url match if strict.
                # Yachtpaint base: .../nl/nl/bootverf. Categories are .../nl/nl/products/filters/...
                # So pure base_url startswith might be too strict if they jump to /products/.
                # We'll check if it's at least the same domain.

                from urllib.parse import urlparse
                if urlparse(sub_url).netloc != urlparse(self.base_url).netloc:
                    continue

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
        # Store the categories
        categories: List[Category] = []

        # Shorthand the selectors config
        selectors = self.config.category.selectors

        # Get all elements
        elements = page.query_selector_all(selectors.selector)

        for el in elements:
            name = self._get_text(el, selectors.name)

            url = self._process_url(
                base_url=self.config.category.processors.base_url,
                page_url=page.url,
                raw=self._get_attr(el, selectors.url, 'href'),
            )

            category = Category(
                name=name,
                url=url,
            )

            categories.append(category)

        return categories

    def get_products(self, page: Page) -> List[Product]:
        # Store the products
        products: List[Product] = []

        # Shorthand the selectors config
        selectors = self.config.product.selectors

        # Get all elements
        elements = page.query_selector_all(selectors.selector)

        for el in elements:
            name = self._get_text(el, selectors.name)
            url = self._get_attr(el, selectors.url, "href")

            url = self._process_url(
                base_url=self.config.product.processors.base_url,
                page_url=page.url,
                raw=url,
            )

            product = Product(
                name=name,
                url=url,
            )

            products.append(product)

        return products
