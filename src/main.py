import logging
from src.models.wiki_scraper import WikiScraper
from src.models.realestate_scraper import RealEstateScraper


def run_wiki_scraper():
    logging.info("Starting WikiScraper...")
    scraper = WikiScraper()
    scraper.run()
    scraper.save_data("wiki_data.json", folder="data")


def run_realestate_scraper():
    logging.info("Starting RealEstateScraper...")
    scraper = RealEstateScraper()
    scraper.run()
    scraper.save_data()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    print("Select scraper to run:")
    print("1. Wikipedia Scraper")
    print("2. Real Estate Scraper (BogotaRealEstate)")
    choice = input("Enter 1 or 2: ").strip()

    if choice == "1":
        run_wiki_scraper()
    elif choice == "2":
        run_realestate_scraper()
    else:
        print("Invalid choice.")
