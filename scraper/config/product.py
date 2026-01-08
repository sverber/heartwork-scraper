from typing import Optional

from pydantic import BaseModel


class ProductSelectors(BaseModel):
    selector: str
    url: str
    name: str
    description: Optional[str] = None
    image: Optional[str] = None


class ProductListSelectors(BaseModel):
    selector: str
    url: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    image: Optional[str] = None


class ProductDetailSelectors(BaseModel):
    title: str
    description: str
    image: str


class ProductProcessors(BaseModel):
    base_url: Optional[str] = None


class ProductConfig(BaseModel):
    list: ProductListSelectors
    detail: Optional[ProductDetailSelectors] = None
    processors: ProductProcessors
