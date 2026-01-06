from typing import List
from scraper.base import BaseScraper
from scraper.models import Category, Product

class ExampleScraper(BaseScraper):
    def scrape(self) -> Category:
        # Simulate a scrape
        root = Category(name="Root", url=f"{self.base_url}/")
        
        cat1 = Category(name="Electronics", url=f"{self.base_url}/electronics")
        cat1.products.append(Product(name="Laptop", url=f"{self.base_url}/laptop"))
        
        cat2 = Category(name="Books", url=f"{self.base_url}/books")
        cat2.products.append(Product(name="Python Guide", url=f"{self.base_url}/python-guide"))
        
        root.subcategories.extend([cat1, cat2])
        return root

    def get_categories(self, url: str) -> List[Category]:
        return []

    def get_products(self, url: str) -> List[Product]:
        return []
