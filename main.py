from pathlib import Path

from scraper.config.base import ScraperConfig
from scraper.config.category import CategoryListSelectors, CategoryConfig, CategoryProcessors
from scraper.config.product import ProductListSelectors, ProductDetailSelectors, ProductProcessors, ProductConfig
from scraper.configurable_scraper import ConfigurableScraper
from scraper.sites.epifanes_attributes import EpifanesAttributeExtractor
from scraper.sites.epifanes_files import EpifanesFileExtractor


def run_one(site_key: str, selected: dict):
    print(f"Scraping site: {site_key}")

    scraper = ConfigurableScraper(
        base_url=selected["base_url"],
        config=selected["config"],
        attribute_extractor=selected.get("attribute_extractor"),
        file_extractor=selected.get("file_extractor"),
        headless=True,
    )

    root_category = scraper.scrape()

    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    output_file = output_dir / f"output_{site_key}.json"
    output_file.write_text(root_category.model_dump_json(indent=2))

    print(f"Scrape finished. Data saved to {output_file}")

def main():
    # Define available configurations
    configs = {
        "epifanes_binnenvaart": {
            "base_url": "https://www.epifanes.nl/nl/onze-collecties/epifanes-binnenvaart",
            "attribute_extractor": EpifanesAttributeExtractor(),
            "file_extractor": EpifanesFileExtractor(),
            "config": ScraperConfig(
                category=CategoryConfig(
                    list=CategoryListSelectors(
                        selector="a.OneItem:not(.OneProduct)[href]",
                        url=":scope",
                        name="h2",
                        description="p",
                        image="img",
                    ),
                    detail=None,  # optional / unknown
                    processors=CategoryProcessors(
                        base_url="https://www.epifanes.nl/nl/"
                    ),
                ),
                product=ProductConfig(
                    list=ProductListSelectors(
                        selector="a.OneItem.OneProduct[href]",
                        url=":scope",
                        name="h3[itemprop='name']",
                        description=".QuickInfo p:first-of-type",
                        image="img",
                    ),
                    # @todo: product detail selector is not yet completed
                    detail=ProductDetailSelectors(
                        # placeholders until we inspect a product detail page
                        title="h1, h2[itemprop='name'], h1[itemprop='name']",
                        description="[itemprop='description'], .product-description, .description, main p",
                        image="img[itemprop='image'], img",
                    ),
                    processors=ProductProcessors(
                        base_url="https://www.epifanes.nl/nl/"
                    ),
                ),
            ),
        },
        "epifanes_pleziervaart": {
            "base_url": "https://www.epifanes.nl/nl/onze-collecties/epifanes-pleziervaart",
            "attribute_extractor": EpifanesAttributeExtractor(),
            "config": ScraperConfig(
                category=CategoryConfig(
                    list=CategoryListSelectors(
                        selector="a.OneItem:not(.OneProduct)[href]",
                        url=":scope",
                        name="h2",
                        description="p",
                        image="img",
                    ),
                    detail=None,  # optional / unknown
                    processors=CategoryProcessors(
                        base_url="https://www.epifanes.nl/nl/"
                    ),
                ),
                product=ProductConfig(
                    list=ProductListSelectors(
                        selector="a.OneItem.OneProduct[href]",
                        url=":scope",
                        name="h3[itemprop='name']",
                        description=".QuickInfo p:first-of-type",
                        image="img",
                    ),
                    # @todo: product detail selector is not yet completed
                    detail=ProductDetailSelectors(
                        # placeholders until we inspect a product detail page
                        title="h1, h2[itemprop='name'], h1[itemprop='name']",
                        description="[itemprop='description'], .product-description, .description, main p",
                        image="img[itemprop='image'], img",
                    ),
                    processors=ProductProcessors(
                        base_url="https://www.epifanes.nl/nl/"
                    ),
                ),
            ),
        },
        "international_pc": {
            "base_url": "https://www.international-pc.com/en/product-category",
            "config": ScraperConfig(
                category=CategoryConfig(
                    list=CategoryListSelectors(
                        selector="a.a2-text-link[href^='/en/products/filters/']",
                        url=":scope",
                        name=".text-link-label span",
                        description=None,
                        image=None,
                    ),
                    detail=None,
                    processors=CategoryProcessors(
                        base_url="https://www.international-pc.com"
                    ),
                ),
                product=ProductConfig(
                    list=ProductListSelectors(
                        selector="article.m24-product-card-c",
                        url="a.clickable-card",
                        name=".product-title .js-camp-temp-text-color",
                        description=".product-description .js-camp-temp-text-color",
                        image=None,
                    ),
                    # @todo: product detail selector is not yet completed
                    detail=ProductDetailSelectors(
                        # placeholders until we inspect a product detail page
                        title="h1, [itemprop='name'], .product-title",
                        description="[itemprop='description'], .product-description, main p",
                        image="img[itemprop='image'], img",
                    ),
                    processors=ProductProcessors(
                        base_url="https://www.international-pc.com"
                    ),
                ),
            ),
        },
        "yachtpaint": {
            "base_url": "https://www.international-yachtpaint.com/nl/nl/bootverf",
            "config": ScraperConfig(
                category=CategoryConfig(
                    list=CategoryListSelectors(
                        selector="a.a2-text-link[href^='/nl/nl/products/filters/']",
                        url=":scope",
                        name=".text-link-label span",
                        description=None,
                        image=None,
                    ),
                    detail=None,
                    processors=CategoryProcessors(
                        base_url="https://www.international-yachtpaint.com"
                    ),
                ),
                product=ProductConfig(
                    list=ProductListSelectors(
                        selector="div.product-cardB",
                        url="a[href^='/nl/nl/products/']",
                        name="h2.product-title",
                        description="p.product-description",
                        image="img.image-center",
                    ),
                    # @todo: product detail selector is not yet completed
                    detail=ProductDetailSelectors(
                        title="h1",
                        description="[data-component*='product'] p, .product-description",
                        image="img[itemprop='image'], img",
                    ),
                    processors=ProductProcessors(
                        base_url="https://www.international-yachtpaint.com"
                    ),
                ),
            )
        }
    }

    # Determine site(s) to scrape (comment one)
    site_key: str | None = "epifanes_binnenvaart"
    # site_key: str | None = None

    if not site_key:
        for key, selected in configs.items():
            run_one(key, selected)
        return

    if site_key not in configs:
        print(f"Unknown site: {site_key}. Available: {', '.join(configs.keys())}")
        return

    run_one(site_key, configs[site_key])


if __name__ == "__main__":
    main()