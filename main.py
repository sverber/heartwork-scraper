from scraper.config import ScraperConfig
from scraper.configurable_scraper import ConfigurableScraper


def main():
    # Epifanes Configuration
    config = ScraperConfig(
        category_selector="a.OneItem:not(.OneProduct)",
        product_selector="a.OneProduct"
    )
    
    # Instantiate the scraper
    # headless=False as requested by user
    scraper = ConfigurableScraper(
        base_url="https://www.epifanes.nl/nl/onze-collecties/epifanes-pleziervaart",
        config=config,
        headless=True 
    )
    
    # Run the scraper
    print("Starting scrape...")
    root_category = scraper.scrape()
    
    # Save to JSON
    with open("output.json", "w") as f:
        f.write(root_category.model_dump_json(indent=2))
        
    print("Scrape finished. Data saved to output.json")

if __name__ == "__main__":
    main()
