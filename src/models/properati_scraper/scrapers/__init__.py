"""
Scraper modules for Properati data extraction.
"""

from src.models.properati_scraper.scrapers.base_scraper import (
    Scraper,
    SeleniumBaseScraper,
)
from src.models.properati_scraper.scrapers.listing_scraper import ListingScraper
from src.models.properati_scraper.scrapers.detail_scraper import DetailScraper
from src.models.properati_scraper.scrapers.project_scraper import ProjectScraper

__all__ = [
    "Scraper",
    "SeleniumBaseScraper",
    "ListingScraper",
    "DetailScraper",
    "ProjectScraper",
]
