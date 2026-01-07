import re
from typing import List

from playwright.sync_api import Page

from scraper.attributes import ProductAttributeExtractor
from scraper.models import ProductAttribute


class EpifanesAttributeExtractor(ProductAttributeExtractor):
    def extract(self, page: Page) -> List[ProductAttribute]:
        attributes: List[ProductAttribute] = []

        container = page.query_selector("div[itemprop='description']")
        if not container:
            return attributes

        blocks = container.query_selector_all("div.PI_contentTexts")

        for block in blocks:
            # Attribute name
            header = block.query_selector("h4")
            if not header:
                continue

            name = header.inner_text().strip().rstrip(":")

            # Attribute value
            value_el = block.query_selector("p")
            if not value_el:
                continue

            raw_value = value_el.inner_text().strip()
            if not raw_value:
                continue

            value = re.sub(r"\s+", " ", raw_value)

            attributes.append(
                ProductAttribute(
                    name=name,
                    values=[value],
                )
            )

        return attributes
