import os
import sys
import logging
from datetime import datetime

# Ensure that src/ is in sys.path
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# Imports (packages)
from models.wiki_scraper import WikiScraper
from models.properati_scraper.properati_main import ProperatiScraper


def setup_logging(verbose=False):
    """
    Configure the logging system.

    Args:
        verbose: If True, show all logs in console.
                 If False, only show WARNING+ logs in console.
    """
    # Create logs folder if it does not exist
    log_folder = "logs"
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)

    # Log file with timestamp
    log_file = os.path.join(
        log_folder, f"scraper_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    )

    # Remove previous handlers
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    # File handler - saves EVERYTHING
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s [%(levelname)s] %(message)s", "%Y-%m-%d %H:%M:%S"
        )
    )

    # Console handler - configurable
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO if verbose else logging.WARNING)
    console_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s [%(levelname)s] %(message)s", "%Y-%m-%d %H:%M:%S"
        )
    )

    # Configure logging root
    logging.basicConfig(level=logging.INFO, handlers=[file_handler, console_handler])

    if verbose:
        print(f"Log file: {log_file}")
        print(f"Verbose mode: Showing all logs")
    else:
        print(f"Log file: {log_file}")
        print(f"Silent mode: Only warnings in console (full logs in file)")


def show_menu():
    print("\n==============================")
    print("          SELECT SCRAPER")
    print("==============================")
    print("1) Properati Scraper")
    print("2) Wiki Scraper")
    print("0) Exit\n")
    return input("Select an option: ").strip()


def run_properati():
    """Run ProperatiScraper with full configuration."""
    print("\n➡ Running ProperatiScraper...\n")

    # Ask logging mode
    verbose_input = input("Show all logs in console? (y/n) [n]: ").strip().lower()
    verbose = verbose_input == "y"

    # Configure logging
    setup_logging(verbose=verbose)

    try:
        print("\n" + "=" * 60)
        print("SCRAPER CONFIGURATION")
        print("=" * 60)

        # Create scraper instance
        scraper = ProperatiScraper(
            mode="venta",  # "venta", "arriendo", or "todos"
            max_pages=1,  # Number of pages to scrape
            headless=True,  # Run without graphical interface
            requests_per_minute=30,  # Scraping speed
            scrape_project_units=True,  # Scrape project units
        )

        print(f"Mode: {scraper.mode}")
        print(f"Max pages: {scraper.max_pages}")
        print(f"Headless: {scraper.ctrl.headless}")
        print(f"Requests/minute: {scraper.requests_per_minute}")
        print("=" * 60 + "\n")

        print("Starting scraping...")

        # Run scraper
        scraper.run()

        # Show summary
        print("\n" + "=" * 60)
        print("EXECUTION SUMMARY")
        print("=" * 60)
        print(f"Total properties processed: {len(scraper.data)}")
        print(f"Files saved in: realestate_data/")
        print("=" * 60)

    except KeyboardInterrupt:
        logging.warning("\n\nProcess interrupted by user (Ctrl+C)")
        print("\nScraping stopped. Partial data has been saved.")

    except Exception as e:
        logging.error(f"\nCritical error during execution: {e}", exc_info=True)
        print(f"\nError: {e}")
        print("Check the log file for more details.")

    finally:
        print("\n✓ ProperatiScraper finished.\n")


def run_wiki():
    """Run WikiScraper."""
    print("\n➡ Running WikiScraper...\n")

    setup_logging(verbose=False)

    try:
        scraper = WikiScraper()
        result = scraper.run()

        print("\n" + "=" * 60)
        print("WIKISCRAPER RESULT")
        print("=" * 60)

        if result and "data" in result and result["data"]:
            data_list = result["data"]

            # Show in console
            for item in data_list:
                print(f"\nTitle: {item.get('title', 'N/A')}")
                content = item.get("content", "N/A")
                print(
                    f"Content: {content[:200]}..."
                    if len(content) > 200
                    else f"Content: {content}"
                )
                if item.get("error"):
                    print(f"Error: {item.get('error')}")

            # Save CSV
            import pandas as pd
            from datetime import datetime

            # Create folder if needed
            data_folder = "wiki_data"
            if not os.path.exists(data_folder):
                os.makedirs(data_folder)

            # Create DataFrame
            df = pd.DataFrame(data_list)

            # Add timestamp
            df["extraction_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Save CSV
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            csv_path = os.path.join(data_folder, f"wiki_data_{timestamp}.csv")
            df.to_csv(csv_path, index=False, encoding="utf-8-sig")

            # Save JSON
            json_path = os.path.join(data_folder, f"wiki_data_{timestamp}.json")
            import json

            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(data_list, f, ensure_ascii=False, indent=2)

            print("\n" + "=" * 60)
            print("FILES SAVED")
            print("=" * 60)
            print(f"CSV: {csv_path}")
            print(f"JSON: {json_path}")
            print(f"Total records: {len(data_list)}")
        else:
            print("\nNo data found to save")

        print("=" * 60)
        print("\nWikiScraper finished.\n")

    except Exception as e:
        logging.error(f"Error in WikiScraper: {e}", exc_info=True)
        print(f"\nError: {e}")
        print("Check the log file for more details.")


def main():
    """Main program function."""
    while True:
        option = show_menu()

        if option == "1":
            run_properati()

        elif option == "2":
            run_wiki()

        elif option == "0":
            print("\n Leaving the program")
            break

        else:
            print("\n Invalid option. Please select: 1, 2, or 0.")

        # Ask to continue or exit
        if option in ["1", "2"]:
            cont = input("\nDo you want to continue? (y/n): ").strip().lower()
            if cont != "y":
                print("\n Leaving the program")
                break


if __name__ == "__main__":
    main()
