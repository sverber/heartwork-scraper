from typing import Optional, List

from pydantic import BaseModel

from scraper.config.pagination import PaginationConfig


class CategoryListSelectors(BaseModel):
    selector: str
    url: str
    name: str
    description: Optional[str] = None
    image: Optional[str] = None
    pagination: Optional[PaginationConfig] = None


class CategoryDetailSelectors(BaseModel):
    title: str
    description: Optional[str] = None
    image: Optional[str] = None


class CategoryProcessors(BaseModel):
    base_url: Optional[str] = None


class CategoryConfig(BaseModel):
    lists: List[CategoryListSelectors]
    detail: Optional[CategoryDetailSelectors] = None
    processors: CategoryProcessors
