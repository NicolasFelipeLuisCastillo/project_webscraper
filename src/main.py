from models.wiki_scraper import WikiScraper
from models.realestate_scraper import RealEstateScraper


def main():
    wiki = WikiScraper("example")
    wiki.run()

    real_estate = RealEstateScraper("example")
    real_estate.run()


if __name__ == "__main__":
    main()
