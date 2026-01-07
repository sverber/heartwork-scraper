import sys

from scraper.config.base import ScraperConfig
from scraper.config.category import CategoryListSelectors, CategoryConfig, CategoryProcessors
from scraper.config.product import ProductListSelectors, ProductDetailSelectors, ProductProcessors, ProductConfig
from scraper.configurable_scraper import ConfigurableScraper
from scraper.sites.epifanes_attributes import EpifanesAttributeExtractor


def main():
    # Define available configurations
    configs = {
        "epifanes_binnenvaart": {
            "base_url": "https://www.epifanes.nl/nl/onze-collecties/epifanes-binnenvaart",
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

    # Determine site to scrape
    site_key = "epifanes_binnenvaart"  # default

    if len(sys.argv) > 1:
        site_key = sys.argv[1]

    if site_key not in configs:
        print(f"Unknown site: {site_key}. Available: {', '.join(configs.keys())}")
        return

    print(f"Scraping site: {site_key}")
    selected = configs[site_key]

    # Instantiate the scraper
    scraper = ConfigurableScraper(
        base_url=selected["base_url"],
        attribute_extractor=selected["attribute_extractor"],
        config=selected["config"],
        headless=False
    )

    # Run the scraper
    root_category = scraper.scrape()

    # Save to JSON
    output_file = f"output_{site_key}.json"
    with open(output_file, "w") as f:
        f.write(root_category.model_dump_json(indent=2))

    print(f"Scrape finished. Data saved to {output_file}")


if __name__ == "__main__":
    main()
