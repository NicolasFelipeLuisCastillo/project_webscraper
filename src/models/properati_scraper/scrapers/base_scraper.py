"""
Base scraper class with common functionality.
"""

import logging
import requests
import json
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from src.models.properati_scraper.utils.helpers import human_pause, detect_captcha


class Scraper:
    """Base scraper class with common functionality for both requests and selenium."""

    def __init__(self, base_url=None, endpoints=None):
        self.base_url = base_url or ""
        self.endpoints = endpoints or []
        self.session = requests.Session()
        self.data = []

    def fetch_html(self, endpoint: str) -> str:
        """Fetch HTML content using requests."""
        url = f"{self.base_url}{endpoint}"
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Connection": "keep-alive",
        }

        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            logging.error(f"Request failed: {e}")
            return ""

    def parse(self, html):
        """Parse method to be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement the parse() method.")

    def save_data(self, filename, folder="data"):
        """Save data to JSON file."""
        if not self.data:
            logging.info("No data to save.")
            return

        if not os.path.exists(folder):
            os.makedirs(folder)

        path = os.path.join(folder, filename)

        try:
            with open(path, "w", encoding="utf-8") as file:
                json.dump(self.data, file, indent=4, ensure_ascii=False)
            logging.info(f"Data successfully saved to {path}")
        except IOError as error:
            logging.error(f"Error saving data: {error}")

    def run(self):
        """Main run method for requests-based scraping."""
        if not self.endpoints:
            logging.info("No endpoints defined.")
            return

        for endpoint in self.endpoints:
            html = self.fetch_html(endpoint)
            if not html:
                continue

            parsed_items = self.parse(html)
            if parsed_items:
                if isinstance(parsed_items, list):
                    self.data.extend(parsed_items)
                else:
                    self.data.append(parsed_items)

        logging.info(f"Scraping completed. Total items: {len(self.data)}")


class SeleniumBaseScraper:
    """Base class for selenium-based scrapers with common functionality."""

    def __init__(self, driver):
        self.driver = driver

    def wait_for_page_load(self, timeout=15):
        """Wait for page to load completely."""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            return True
        except Exception as e:
            logging.warning(f"Timeout waiting for page: {e}")
            return False

    def scrape_with_captcha_protection(self, url, timeout=15):
        """
        Scrape URL with CAPTCHA protection.

        Args:
            url: URL to scrape
            timeout: Timeout for page load

        Returns:
            Page HTML or None if CAPTCHA detected
        """
        try:
            self.driver.get(url)
            if not self.wait_for_page_load(timeout):
                return None

            human_pause(1, 0.5)
            html = self.driver.page_source

            if detect_captcha(html):
                logging.warning(f"CAPTCHA detected at: {url}")
                return None

            return html

        except Exception as e:
            logging.warning(f"Error loading page {url}: {e}")
            return None

    def scroll_page(self, scroll_pause=1.2, max_scrolls=6):
        """Scroll page to load dynamic content."""
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        for _ in range(max_scrolls):
            self.driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);"
            )
            human_pause(scroll_pause, 0)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
