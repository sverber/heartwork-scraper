from typing import Optional

from pydantic import BaseModel


class CategoryListSelectors(BaseModel):
    selector: str
    url: str
    name: str
    description: Optional[str] = None
    image: Optional[str] = None


class CategoryDetailSelectors(BaseModel):
    title: str
    description: Optional[str] = None
    image: Optional[str] = None


class CategoryProcessors(BaseModel):
    base_url: Optional[str] = None


class CategoryConfig(BaseModel):
    list: CategoryListSelectors
    detail: Optional[CategoryDetailSelectors] = None
    processors: CategoryProcessors
