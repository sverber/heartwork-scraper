import sys
from platform import processor

from scraper.config import ScraperConfig, CategoryConfig, ProductConfig, CategorySelectors, ProductSelectors, \
    CategoryProcessors, ProductProcessors
from scraper.configurable_scraper import ConfigurableScraper


def main():
    # Define available configurations
    configs = {
        "epifanes": {
            "base_url": "https://www.epifanes.nl/nl/onze-collecties/epifanes-pleziervaart",
            "config": ScraperConfig(
                category=CategoryConfig(
                    selectors=CategorySelectors(
                        selector="a.OneItem:not(.OneProduct)[href]",
                        url=":scope",
                        name="h2",
                        description="p",
                        image="img",
                    ),
                    processors=CategoryProcessors(
                        base_url="https://www.epifanes.nl/nl/"
                    )
                ),
                product=ProductConfig(
                    selectors=ProductSelectors(
                        selector="a.OneItem.OneProduct[href]",
                        url=":scope",
                        name="h3[itemprop='name']",
                        description=".QuickInfo p:first-of-type",
                        image="img",
                    ),
                    processors=ProductProcessors(
                        base_url="https://www.epifanes.nl/nl/"
                    )
                ),
            )
        },
        "yachtpaint": {
            "base_url": "https://www.international-yachtpaint.com/nl/nl/bootverf",
            "config": ScraperConfig(
                category=CategoryConfig(
                    selectors=CategorySelectors(
                        # Category tile: the clickable <a> inside the <li> card
                        selector="li.product-category-card-b--list-item a.a2-text-link[href*='/products/filters/']",
                        url=":scope",  # read href from the <a>
                        name=".text-link-label span",  # "Aflakken"
                        description=":scope + span.subTitle",  # sibling subtitle after the <a>
                        image="img[itemprop='image']",  # category image
                    ),
                    processors=CategoryProcessors(
                        base_url="https://www.international-yachtpaint.com"
                    )
                ),
                product=ProductConfig(
                    selectors=ProductSelectors(
                        # Product tile: the card root
                        selector="div.product-cardB",
                        # URL is NOT on the outer product-link anchor (it has no href);
                        # it is on the "Bekijk product" anchor
                        url="a[href*='/products/']:has(span:text('Bekijk product'))",
                        name="h2.product-title",
                        description="p.product-description",
                        image="img.image-center",
                    ),
                    processors=ProductProcessors(
                        base_url="https://www.international-yachtpaint.com"
                    )
                )
            )
        }
    }

    # Determine site to scrape
    site_key = "yachtpaint"  # default
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
        config=selected["config"],
        headless=True
    )

    # Run the scraper
    print("Starting scrape...")
    root_category = scraper.scrape()

    # Save to JSON
    output_file = f"output_{site_key}.json"
    with open(output_file, "w") as f:
        f.write(root_category.model_dump_json(indent=2))

    print(f"Scrape finished. Data saved to {output_file}")


if __name__ == "__main__":
    main()
