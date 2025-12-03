"""
Main entry point for Properati scraper.
"""

import os
import sys
import time
import random
import logging
from datetime import datetime
from bs4 import BeautifulSoup

# Add the parent directory to Python path to allow absolute imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Now use absolute imports
from models.properati_scraper.drivers import WebDriverController
from models.properati_scraper.scrapers.base_scraper import Scraper, SeleniumBaseScraper
from models.properati_scraper.scrapers.listing_scraper import ListingScraper
from models.properati_scraper.scrapers.detail_scraper import DetailScraper
from models.properati_scraper.scrapers.project_scraper import ProjectScraper
from models.properati_scraper.utils.helpers import ensure_folder_exists, human_pause
from models.properati_scraper.utils.file_handlers import DataHandler
from models.properati_scraper.config import (
    BASE_URL,
    DATA_FOLDER,
    BACKUP_INTERVAL,
    DEFAULT_MAX_PAGES,
    DEFAULT_REQUESTS_PER_MINUTE,
    DEFAULT_HEADLESS,
)


class ProperatiScraper(Scraper):
    """Main scraper class coordinating all scraping activities."""

    def __init__(
        self,
        mode="todos",
        max_pages=DEFAULT_MAX_PAGES,
        headless=DEFAULT_HEADLESS,
        requests_per_minute=DEFAULT_REQUESTS_PER_MINUTE,
        scrape_project_units=True,
    ):
        # Initialize parent Scraper class
        super().__init__(base_url=BASE_URL)

        self.mode = mode
        self.max_pages = max_pages
        self.requests_per_minute = requests_per_minute
        self.scrape_project_units = scrape_project_units

        # Initialize components
        self.ctrl = WebDriverController(headless=headless)
        self.data_handler = DataHandler()
        self.listing_scraper = ListingScraper(self.ctrl.driver)
        self.detail_scraper = DetailScraper(self.ctrl.driver)
        self.project_scraper = ProjectScraper(self.ctrl.driver)

        # Data storage
        self.data = []
        self.properties_processed = 0
        self.backup_counter = 0

    def parse(self, html):
        """
        Parse method required by base Scraper class.
        This is mainly for requests-based parsing, but we use selenium primarily.
        """
        # Since we primarily use selenium, this method can be a stub
        # or you can implement requests-based parsing here if needed
        logging.info("Using selenium-based parsing instead of requests")
        return []

    def _handle_captcha(self):
        """Handle CAPTCHA detection with browser restart."""
        logging.warning("CAPTCHA detected! Taking measures...")

        wait_time = random.randint(180, 300)
        logging.info(f"Waiting {wait_time} seconds to avoid blocking...")

        for i in range(wait_time, 0, -30):
            if i > 0:
                logging.info(f"Waiting {i} more seconds...")
                time.sleep(min(30, i))

        logging.info("Restarting browser...")
        self.ctrl.close()
        human_pause(5, 3)

        # Reinitialize all components with new driver
        self.ctrl = WebDriverController(headless=self.ctrl.headless)
        self.listing_scraper = ListingScraper(self.ctrl.driver)
        self.detail_scraper = DetailScraper(self.ctrl.driver)
        self.project_scraper = ProjectScraper(self.ctrl.driver)

        logging.info("Browser restarted, continuing...")

    def _save_data_incremental(self, new_properties_count=0, force_save=False):
        """
        Save data incrementally at specified intervals.

        Args:
            new_properties_count: Number of new properties processed
            force_save: Whether to force save regardless of interval
        """
        if not self.data:
            return

        # Update counters
        self.properties_processed += new_properties_count
        self.backup_counter += new_properties_count

        # Save at specified interval or if forced
        if force_save or self.backup_counter >= BACKUP_INTERVAL:
            self.data_handler.save_data(self.data)
            self.backup_counter = 0

    def run(self):
        """Main scraping execution method."""
        try:
            ensure_folder_exists(DATA_FOLDER)
            sections = ["venta", "arriendo"] if self.mode == "todos" else [self.mode]

            total_properties = 0
            captcha_encountered = False

            for section in sections:
                if captcha_encountered:
                    logging.warning("Skipping section due to previous CAPTCHA")
                    break

                logging.info(f"Scraping section: {section}")

                for page in range(1, self.max_pages + 1):
                    if captcha_encountered:
                        logging.warning(
                            f"Skipping remaining pages of {section} due to CAPTCHA"
                        )
                        break

                    logging.info(f"Processing page {page} of {section}")

                    # Build URL
                    if page == 1:
                        url = f"{self.base_url}/s/{section}"
                    else:
                        url = f"{self.base_url}/s/{section}/{page}"

                    # Extract links with CAPTCHA protection
                    html = self.detail_scraper.scrape_with_captcha_protection(url)
                    if html is None:
                        captcha_encountered = True
                        self._handle_captcha()
                        continue

                    soup = BeautifulSoup(html, "html.parser")

                    if self.listing_scraper.check_pagination_limit(soup, page):
                        logging.info(f"Pagination limit reached at page {page}")
                        break

                    # Extract links
                    links = self.listing_scraper.extract_links_from_soup(soup)

                    if not links:
                        logging.info(f"No links found on page {page}")
                        break

                    success_count = 0
                    page_properties = []

                    for i, link in enumerate(links, start=1):
                        if captcha_encountered:
                            break

                        # Pause between requests
                        time_between_requests = 60 / self.requests_per_minute
                        time.sleep(time_between_requests + random.uniform(0.5, 2))

                        logging.info(f"({i}/{len(links)}) Processing: {link}")

                        # Handle projects vs individual properties
                        if "/proyecto/" in link and self.scrape_project_units:
                            # Scrape complete project with its units
                            project_data = (
                                self.project_scraper.scrape_project_with_units(link)
                            )
                            if project_data:
                                # Add project properties to data
                                self.data.extend(project_data)
                                success_count += len(project_data)
                                total_properties += len(project_data)

                                # Save incrementally after processing project
                                self._save_data_incremental(len(project_data))

                        else:
                            # Normal individual property
                            property_result = self.detail_scraper.scrape_property(link)
                            if property_result and not property_result.get("Error"):
                                self.data.append(property_result)
                                page_properties.append(property_result)
                                success_count += 1
                                total_properties += 1

                                # Save incrementally after each individual property
                                self._save_data_incremental(1)
                            else:
                                logging.warning("Property with invalid data")
                                if not property_result.get("Error"):
                                    property_result["Error"] = "Invalid data or CAPTCHA"
                                self.data.append(property_result)
                                page_properties.append(property_result)

                                # Also count properties with error for backup
                                self._save_data_incremental(1)

                    logging.info(
                        f"Page {page} completed: {success_count} successful records"
                    )

                    # Save incrementally after each complete page
                    if page_properties:
                        logging.info(
                            f"Page {page} summary: {len(page_properties)} properties processed"
                        )
                        self._save_data_incremental(force_save=True)

                    if page < self.max_pages and not captcha_encountered:
                        pause_time = random.randint(10, 20)
                        logging.info(f"Pause of {pause_time} seconds...")
                        time.sleep(pause_time)

            # Save final data and statistics
            self.data_handler.save_data(self.data)
            self.data_handler.log_statistics(self.data)

            if captcha_encountered:
                logging.warning(
                    "Scraping interrupted due to CAPTCHA. Some data was saved."
                )
            else:
                logging.info("Scraping completed successfully!")

        except Exception as e:
            logging.error(f"General scraping error: {e}")
            try:
                # Try to save collected data
                if self.data:
                    self._save_data_incremental(force_save=True)
                    self.data_handler.save_data(self.data)
                    self.data_handler.log_statistics(self.data)
            except Exception as save_error:
                logging.error(f"Error saving data: {save_error}")
        finally:
            self.ctrl.close()
            logging.info("Scraping finished.")


def main():
    """Main function to run the scraper when executed directly."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Initialize and run scraper
    scraper = ProperatiScraper(
        mode="venta",
        max_pages=2,
        headless=False,
        requests_per_minute=30,
        scrape_project_units=True,
    )
    scraper.run()
