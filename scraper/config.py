from typing import Optional

from pydantic import BaseModel


class CategorySelectors(BaseModel):
    selector: str
    url: str
    name: str
    description: Optional[str] = None
    image: Optional[str] = None

class CategoryProcessors(BaseModel):
    base_url: Optional[str] = None

class CategoryConfig(BaseModel):
    selectors: CategorySelectors
    processors: CategoryProcessors

class ProductSelectors(BaseModel):
    selector: str
    url: str
    name: str
    description: Optional[str] = None
    image: Optional[str] = None

class ProductProcessors(BaseModel):
    base_url: Optional[str] = None


class ProductConfig(BaseModel):
    selectors: ProductSelectors
    processors: ProductProcessors

class ScraperConfig(BaseModel):
    category: CategoryConfig
    product: ProductConfig
