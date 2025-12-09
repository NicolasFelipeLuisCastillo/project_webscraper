"""
Listing page scraper for extracting property links.
"""

import logging
from urllib.parse import urljoin
from bs4 import BeautifulSoup

from src.models.properati_scraper.scrapers.base_scraper import SeleniumBaseScraper
from src.models.properati_scraper.config import BASE_URL, LINK_SELECTORS


class ListingScraper(SeleniumBaseScraper):
    """Scraper for listing pages to extract property links."""

    def __init__(self, driver):
        super().__init__(driver)

    def extract_links_from_soup(self, soup):
        """
        Extract links from BeautifulSoup object.

        Args:
            soup: BeautifulSoup object

        Returns:
            List of property URLs
        """
        links = set()

        for selector in LINK_SELECTORS:
            elements = soup.select(selector)
            for element in elements:
                href = element.get("href") or element.get("data-url")
                if href:
                    full_url = urljoin(BASE_URL, href)
                    if "/detalle/" in full_url or "/proyecto/" in full_url:
                        links.add(full_url)

        return list(links)

    def extract_links(self, url):
        """
        Extract property links from listing page.

        Args:
            url: Listing page URL

        Returns:
            List of property URLs
        """
        logging.info(f"Loading listings: {url}")
        self.driver.get(url)

        if not self.wait_for_page_load(20):
            return []

        self.scroll_page()
        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        links = self.extract_links_from_soup(soup)

        logging.info(f"{len(links)} links found at {url}")
        return links

    def check_pagination_limit(self, soup, page_num):
        """
        Check if pagination limit has been reached.

        Args:
            soup: BeautifulSoup object
            page_num: Current page number

        Returns:
            Boolean indicating if limit reached
        """
        no_results = soup.select(".no-results, .empty-state, .no-listings")
        if no_results:
            return True

        next_buttons = soup.select(
            ".pagination .next:not(.disabled), .pagination .next[disabled]"
        )
        if next_buttons and "disabled" in str(next_buttons[0]):
            return True

        return False
