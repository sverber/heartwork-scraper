from typing import Optional
from pydantic import BaseModel

class ScraperConfig(BaseModel):
    category_selector: str
    product_selector: str
    pagination_selector: Optional[str] = None
    next_page_selector: Optional[str] = None
