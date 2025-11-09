from models import Scraper


def main():
    # Initialize the scraper
    scraper = Scraper(base_url="assad")

    try:
        # Fetch the main page content
        html = scraper.fetch()
        print("Successfully fetched content from:", scraper.base_url)

        # Attempt to parse (will raise NotImplementedError in base class)
        scraper.parse(html)

    except NotImplementedError:
        print("The parse() method is not implemented in the base Scraper class.")
        print("Please create a subclass that overrides it.")
    except Exception as e:
        print("An error occurred during scraping:", str(e))

    finally:
        print("\nExecution finished.")


if __name__ == "__main__":
    main()
