import logging
from scraper_base import Scraper
from driver import WebDriverController
from list_extractor import PropertyListExtractor
from detail_extractor import PropertyDetailExtractor
from exporter import DataExporter

class RealEstateScraper(Scraper):
    """Coordinador principal del scraping."""

    def __init__(self, base_url, max_pages=1, save_every=5):
        super().__init__(base_url)
        self.ctrl = WebDriverController()
        self.list_extractor = PropertyListExtractor(self.ctrl)
        self.detail_extractor = PropertyDetailExtractor(self.ctrl)
        self.exporter = DataExporter()
        self.max_pages = max_pages
        self.save_every = save_every
        self.sales = []
        self.rentals = []

    def run(self):
        sections = {
            "Sales": "https://bogotarealestate.com.co/search?business_type%5B0%5D=for_sale&order_by=created_at&page={}",
            "Rentals": "https://bogotarealestate.com.co/search?business_type%5B0%5D=for_rent&order_by=created_at&page={}"
        }

        try:
            for section, url_template in sections.items():
                for page in range(1, self.max_pages + 1):
                    url = url_template.format(page)
                    listings = self.list_extractor.extract(url)
                    for i, listing in enumerate(listings, 1):
                        detail = self.detail_extractor.extract(listing["URL"], listing["Title"], listing["Price"])
                        (self.sales if section == "Sales" else self.rentals).append(detail)
                        if i % self.save_every == 0:
                            self.exporter.save_all(self.sales, self.rentals)
            self.exporter.save_all(self.sales, self.rentals)
        finally:
            self.ctrl.close()
