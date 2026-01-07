from typing import List, Optional

from pydantic import BaseModel, HttpUrl, Field


class ProductAttribute(BaseModel):
    name: str
    values: List[str] = Field(default_factory=list)

class Product(BaseModel):
    name: str
    url: HttpUrl
    description: Optional[str] = None
    image: Optional[HttpUrl] = None
    attributes: List['ProductAttribute'] = Field(default_factory=list)


class Category(BaseModel):
    name: str
    url: HttpUrl
    description: Optional[str] = None
    image: Optional[HttpUrl] = None

    subcategories: List['Category'] = Field(default_factory=list)
    products: List['Product'] = Field(default_factory=list)

    class Config:
        # Needed for self-referencing model
        arbitrary_types_allowed = True


Category.model_rebuild()
