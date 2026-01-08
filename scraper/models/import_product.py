from typing import List
from typing import Optional

from playwright.sync_api import Page
from pydantic import BaseModel, HttpUrl, Field


class ImportProductAttribute(BaseModel):
    name: str
    value: str


class ImportProduct(BaseModel):
    sku: str = ""
    product_name: str = Field()
    gross_price: Optional[float] = Field(default=None)
    suggested_retail_price: Optional[float] = Field(default=None)
    gtin: Optional[str] = Field(default=None)

    # Category Hierarchy
    level1_id: Optional[str] = Field(default=None)
    level1_name: Optional[str] = Field(default=None)
    level2_id: Optional[str] = Field(default=None)
    level2_name: Optional[str] = Field(default=None)
    level3_id: Optional[str] = Field(default=None)
    level3_name: Optional[str] = Field(default=None)

    configurable_product_description: Optional[str] = Field(default=None)
    product_catalog_references: List[str] = Field(default_factory=list)
    product_display_order: int = Field(default=0)
    category_display_order: int = Field(default=0)

    brand: Optional[str] = Field(default=None)

    # Packaging & Units
    packing_unit: Optional[float] = Field(default=None)
    packing_container: Optional[str] = Field(default=None)
    packing_quantity: Optional[float] = Field(default=None)
    unit: Optional[str] = Field(default=None)

    barcodes: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    search_codes: Optional[List[str]] = Field(default=None)

    active: bool = Field(default=True)
    show_stock: bool = Field(default=True)
    sales_quantity_step: Optional[float] = Field(default=None)

    attributes: List[ImportProductAttribute] = Field(default_factory=list)

    class Config:
        populate_by_name = True
