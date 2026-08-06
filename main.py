from pathlib import Path

from scraper.config.base import ScraperConfig
from scraper.config.category import CategoryListSelectors, CategoryConfig, CategoryProcessors
from scraper.config.pagination import PaginationConfig
from scraper.config.product import ProductListSelectors, ProductDetailSelectors, ProductProcessors, ProductConfig
from scraper.configurable_scraper import ConfigurableScraper
from scraper.sites.epifanes_attributes import EpifanesAttributeExtractor
from scraper.sites.epifanes_files import EpifanesFileExtractor
from scraper.sites import radiushdd


def run_radiushdd():
    output = Path("output") / "radiushdd_custom_subs.csv"
    radiushdd.scrape(output_path=output, headless=True)


def run_one(site_key: str, selected: dict):
    print(f"Scraping site: {site_key}")

    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / f"{site_key}.json"

    scraper = ConfigurableScraper(
        base_url=selected["base_url"],
        config=selected["config"],
        attribute_extractor=selected.get("attribute_extractor"),
        file_extractor=selected.get("file_extractor"),
        headless=True,
        output_path=output_file,
    )

    scraper.scrape()

    print(f"Scrape finished. Data saved to {output_file}")


def main():
    # Define available configurations
    configs = {
        "de-ijssel-coatings": {
            "base_url": "https://www.de-ijssel-coatings.nl",
            "attribute_extractor": None,  # @todo: build the custom attribute extractor
            "file_extractor": None,  # @todo: build the custom file extractor
            "config": ScraperConfig(
                category=CategoryConfig(
                    lists=[
                        # Homepage
                        CategoryListSelectors(
                            selector="a.category-block[href]",
                            url=":scope",
                            name="p",
                        ),
                        # 2. Producten gateway
                        # @todo: add flag to ignore a specific "category" or step like this.
                        CategoryListSelectors(
                            selector="a[href$='/producten']:has(.page-tile .title:has-text('Producten'))",
                            url=":scope",
                            name=".page-tile .title",
                        ),
                        # 3. Product categories
                        CategoryListSelectors(
                            selector="div.products-tab#categories a[href*='/producten/categorie/']",
                            url=":scope",
                            name=".text-center",
                            image="img",
                        )
                    ],
                    processors=CategoryProcessors(
                        base_url="https://www.de-ijssel-coatings.nl",
                    ),
                ),
                product=ProductConfig(
                    list=ProductListSelectors(
                        selector="div.item-full",
                        url=None,
                        name=".title-small",
                        description="div.description span.readmore[style*='display: none'], div.description span.readmore",
                        image="img",
                    ),
                    detail=None,
                    processors=ProductProcessors(
                        base_url="https://www.de-ijssel-coatings.nl",
                    ),
                ),
            )
        },
        "epifanes_binnenvaart": {
            "base_url": "https://www.epifanes.nl/nl/onze-collecties/epifanes-binnenvaart",
            "attribute_extractor": EpifanesAttributeExtractor(),
            "file_extractor": EpifanesFileExtractor(),
            "config": ScraperConfig(
                category=CategoryConfig(
                    lists=[
                        CategoryListSelectors(
                            selector="a.OneItem:not(.OneProduct)[href]",
                            url=":scope",
                            name="h2",
                            description="p",
                            image="img",
                        )
                    ],
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
            "file_extractor": EpifanesFileExtractor(),
            "config": ScraperConfig(
                category=CategoryConfig(
                    lists=[
                        CategoryListSelectors(
                            selector="a.OneItem:not(.OneProduct)[href]",
                            url=":scope",
                            name="h2",
                            description="p",
                            image="img",
                        )
                    ],
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
        "international-pc": {
            "base_url": "https://www.international-pc.com/en/product-category",
            "attribute_extractor": None,  # @todo: build the custom attribute extractor
            "file_extractor": None,  # @todo: build the custom file extractor
            "config": ScraperConfig(
                category=CategoryConfig(
                    lists=[
                        CategoryListSelectors(
                            selector="a.a2-text-link[href^='/en/products/filters/']",
                            url=":scope",
                            name=".text-link-label span",
                            description=None,
                            image=None,
                        )
                    ],
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
                        pagination=PaginationConfig(
                            selector=".m25-pagination",
                        )
                    ),
                    detail=ProductDetailSelectors(
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
            "attribute_extractor": None,  # @todo: build the custom attribute extractor
            "file_extractor": None,  # @todo: build the custom file extractor
            "config": ScraperConfig(
                category=CategoryConfig(
                    lists=[
                        CategoryListSelectors(
                            selector="a.a2-text-link[href^='/nl/nl/products/filters/']",
                            url=":scope",
                            name=".text-link-label span",
                            description=None,
                            image=None,
                        )
                    ],
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
        },
    }

    # Determine site(s) to scrape (comment one)
    # site_key: str | None = "epifanes_binnenvaart"
    # site_key: str | None = "international_pc"
    # site_key: str | None = "de-ijssel-coatings"
    site_key: str | None = "radiushdd"
    # site_key: str | None = None

    if site_key == "radiushdd":
        run_radiushdd()
        return

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
