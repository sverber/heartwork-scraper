from typing import List, Optional

from pydantic import BaseModel, HttpUrl


class Product(BaseModel):
    name: str
    url: HttpUrl
    price: Optional[str] = None
    description: Optional[str] = None
    # Add other fields as needed, e.g., images, sku, etc.


class Category(BaseModel):
    name: str
    url: HttpUrl
    subcategories: List['Category'] = []
    products: List[Product] = []

    class Config:
        # Needed for self-referencing model
        arbitrary_types_allowed = True
