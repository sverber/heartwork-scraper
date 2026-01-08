from pathlib import Path
from typing import List, Set, Optional
from urllib.parse import urlparse

from playwright.sync_api import Page

from scraper.base import BaseScraper
from scraper.config.base import ScraperConfig
from scraper.config.pagination import PaginationConfig
from scraper.models.attributes import ProductAttributeExtractor
from scraper.models.files import ProductFileExtractor
from scraper.models.models import Category, Product, ProductAttribute, ProductFile


class ConfigurableScraper(BaseScraper):
    def __init__(self,
                 base_url: str, config: ScraperConfig,
                 attribute_extractor: ProductAttributeExtractor | None = None,
                 file_extractor: ProductFileExtractor | None = None,
                 headless: bool = True,
                 output_path: Optional[Path] = None
                 ):
        super().__init__(base_url, headless, output_path)
        self.config = config
        self.attribute_extractor = attribute_extractor
        self.file_extractor = file_extractor
        # Use a global set to ensure we never scrape the same URL twice across the whole site
        self.visited_urls: Set[str] = set()

    def _scrape_impl(self) -> Category:
        self.visited_urls = set()
        page = self.browser.new_page()
        page.goto(self.base_url)

        self.root_node = Category(name="Root", url=self.base_url)

        self._traverse(page, self.root_node)

        return self.root_node

    def _traverse(self, page: Page, current_category: Category):
        # Normalize the URL to prevent trailing slash duplicates
        curr_url = str(current_category.url).rstrip('/')
        self.visited_urls.add(curr_url)
        print(f"Traversing [u]: {current_category.url}")

        # 1. Get Subcategories found on this page
        subcategories = self.get_categories(page)
        current_category.subcategories = subcategories

        # 2. Get Products found on this page (handling pagination)
        products = self.get_products(page)
        current_category.products = products

        # 3. Recurse into subcategories
        base_domain = urlparse(self.base_url).netloc

        for subcat in subcategories:
            sub_url = str(subcat.url).rstrip('/')

            # Scope check: Ensure the sub_url belongs to the same domain.
            # This prevents us from wandering off to external links or social media.
            if urlparse(sub_url).netloc != base_domain:
                continue

            # Skip if we already visited this category elsewhere
            if sub_url in self.visited_urls:
                continue

            try:
                # Open a new page for recursion to keep the state of the current page's elements
                sub_page = self.browser.new_page()
                sub_page.goto(str(subcat.url))
                self._traverse(sub_page, subcat)
                sub_page.close()

                # Save progress after returning from a branch
                self.save_checkpoint()
            except Exception as e:
                print(f"Failed to traverse {subcat.url}: {e}")

    def _discover_pagination_urls(self, page: Page, pagination: PaginationConfig) -> List[str]:
        found_urls = []

        # Find the container block (e.g., .m25-pagination)
        container = page.query_selector(pagination.selector)
        if not container:
            return found_urls

        # Find all links inside that specific block
        links = container.query_selector_all("a[href]")
        for link in links:
            # Skip disabled buttons (like 'next' when on the last page)
            cls = link.get_attribute("class") or ""
            if "disabled" in cls:
                continue

            raw_href = link.get_attribute("href")
            full_url = self._process_url(
                base_url=self.config.category.processors.base_url,
                page_url=page.url,
                raw=raw_href,
            )

            if full_url:
                found_urls.append(str(full_url))

        return found_urls

    def get_categories(self, page: Page) -> List[Category]:
        categories: List[Category] = []

        for selectors in self.config.category.lists:
            pages_to_scrape = [page.url]
            scraped_pagination_urls = set()

            while pages_to_scrape:
                current_url = pages_to_scrape.pop(0)
                norm_p_url = current_url.rstrip('/')

                # Avoid re-scraping the same pagination page
                if norm_p_url in scraped_pagination_urls:
                    continue

                # Navigate if we aren't already there
                if page.url.rstrip('/') != norm_p_url:
                    page.goto(current_url)
                    print(f"Traversing [c-pagination]: {current_url}")

                scraped_pagination_urls.add(norm_p_url)

                elements = page.query_selector_all(selectors.selector)

                for el in elements:
                    name = self._get_text(el, selectors.name)
                    raw_url = self._get_attr(el, selectors.url, "href")
                    if not raw_url:
                        continue

                    url = self._process_url(
                        base_url=self.config.category.processors.base_url,
                        page_url=page.url,
                        raw=raw_url,
                    )
                    norm_url = url.rstrip('/')

                    # Deduplicate: Check global visited list and local current list
                    if not url or norm_url in self.visited_urls:
                        continue

                    if any(c.url == url for c in categories):
                        continue

                    image = None
                    if selectors.image:
                        raw_img = self._get_attr(el, selectors.image, "src")
                        image = self._process_url(
                            base_url=self.config.category.processors.base_url,
                            page_url=page.url,
                            raw=raw_img
                        )

                    category = Category(
                        name=name,
                        url=url,
                        description=self._get_text(el, selectors.description) if selectors.description else None,
                        image=image,
                    )

                    categories.append(category)

                # Find new pages from the pagination block
                if selectors.pagination and selectors.pagination.selector:
                    new_pages = self._discover_pagination_urls(page, selectors.pagination)
                    for p_url in new_pages:
                        if p_url.rstrip('/') not in scraped_pagination_urls:
                            pages_to_scrape.append(p_url)

        return categories

    def get_products(self, page: Page) -> List[Product]:
        products: List[Product] = []
        selectors = self.config.product.list

        pages_to_scrape = [page.url]
        scraped_pagination_urls = set()

        while pages_to_scrape:
            current_url = pages_to_scrape.pop(0)
            norm_p_url = current_url.rstrip('/')

            if norm_p_url in scraped_pagination_urls:
                continue

            if page.url.rstrip('/') != norm_p_url:
                page.goto(current_url)
                print(f"Traversing [p]: {current_url}")

            scraped_pagination_urls.add(norm_p_url)

            elements = page.query_selector_all(selectors.selector)

            for el in elements:
                name = self._get_text(el, selectors.name)

                # If no specific URL selector, assume it's the current page
                raw_url = self._get_attr(el, selectors.url, "href") if selectors.url else page.url
                if not raw_url:
                    continue

                url = self._process_url(
                    base_url=self.config.product.processors.base_url,
                    page_url=page.url,
                    raw=raw_url,
                )
                norm_url = url.rstrip('/')

                # Global deduplication: don't scrape product details if we've seen this URL before
                if norm_url in self.visited_urls or any(p.url == url for p in products):
                    continue

                image = None
                if selectors.image:
                    raw_img = self._get_attr(el, selectors.image, "src")
                    image = self._process_url(
                        base_url=self.config.product.processors.base_url,
                        page_url=page.url,
                        raw=raw_img
                    )

                product = Product(
                    name=name,
                    url=url,
                    description=self._get_text(el, selectors.description) if selectors.description else None,
                    image=image,
                )

                # Enrichment opens the detail page for attributes and files
                product = self.enrich_product(product)

                # Add to global visited list AFTER enrichment so it's fully processed
                self.visited_urls.add(norm_url)
                products.append(product)

            # Discover pagination links
            if hasattr(selectors, 'pagination') and selectors.pagination and selectors.pagination.selector:
                new_pages = self._discover_pagination_urls(page, selectors.pagination)
                for p_url in new_pages:
                    if p_url.rstrip('/') not in scraped_pagination_urls:
                        pages_to_scrape.append(p_url)

        return products

    def get_product_attributes(self, page: Page) -> List[ProductAttribute]:
        return self.attribute_extractor.extract(page) if self.attribute_extractor else []

    def get_product_files(self, page: Page) -> List[ProductFile]:
        return self.file_extractor.extract(page) if self.file_extractor else []

    def enrich_product(self, product: Product) -> Product:
        # We use a context manager pattern to ensure pages close even on failure
        detail_page = self.browser.new_page()
        try:
            detail_page.goto(str(product.url))
            product.attributes = self.get_product_attributes(detail_page)
            product.files = self.get_product_files(detail_page)
        finally:
            detail_page.close()

        return product