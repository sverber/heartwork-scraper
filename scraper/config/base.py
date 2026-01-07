from pydantic import BaseModel

from scraper.config.category import CategoryConfig
from scraper.config.product import ProductConfig


class ScraperConfig(BaseModel):
    category: CategoryConfig
    product: ProductConfig
