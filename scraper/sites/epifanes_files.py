from typing import List
from urllib.parse import urljoin, urlparse, parse_qs

from playwright.sync_api import Page

from scraper.models.files import ProductFileExtractor
from scraper.models.models import ProductFile


class EpifanesFileExtractor(ProductFileExtractor):
    def extract(self, page: Page) -> List[ProductFile]:
        files: List[ProductFile] = []

        container = page.query_selector("p#Downloadable")
        if not container:
            return files

        links = container.query_selector_all("a[href*='download.php']")

        for a in links:
            # Skip hidden links
            style = (a.get_attribute("style") or "").lower()
            if "display: none" in style:
                continue

            href = a.get_attribute("href")
            if not href:
                continue

            # Extract the actual filename parameter
            parsed = urlparse(href)
            filename = parse_qs(parsed.query).get("filename", [None])[0]
            if not filename or filename.endswith("/"):
                continue

            url = urljoin(page.url, href)
            name = (a.inner_text() or "").strip() or None

            files.append(
                ProductFile(
                    name=name,
                    url=url,
                    file_type=self._infer_type(filename),
                )
            )

        return files

    def _infer_type(self, filename: str) -> str | None:
        filename = filename.lower()
        for ext in (".pdf", ".jpg", ".jpeg", ".png", ".doc", ".docx"):
            if filename.endswith(ext):
                return ext.lstrip(".")
        return None
