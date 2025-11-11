# realestate_scraper.py
import os
import time
import random
import logging
import sys
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from typing import List, Dict
from src.models.scraper_base import Scraper


# Configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

SAVE_BATCH = 5
PAGE_LOAD_BASE = 3
RAND_DELAY = (0.5, 1.5)
DATA_FOLDER = "realestate_data"
MAX_RETRIES = 3
MAX_PAGES = 1  # Limit pages for testing


def human_pause():
    """Simulate human browsing with a random delay."""
    time.sleep(PAGE_LOAD_BASE + random.uniform(*RAND_DELAY))


def normalize_text(s: str) -> str:
    """Normalize text: lowercase, strip, remove accents and extra spaces."""
    import unicodedata
    if not s:
        return ""
    s2 = s.lower().strip()
    s2 = unicodedata.normalize("NFKD", s2)
    s2 = "".join(ch for ch in s2 if not unicodedata.combining(ch))
    s2 = " ".join(s2.split())
    return s2


def build_page_url_from_template(template: str, page_num: int) -> str:
    """Replace or add the page parameter in the base URL."""
    if "page=" in template:
        parsed = urlparse(template)
        qs = parse_qs(parsed.query, keep_blank_values=True)
        qs["page"] = [str(page_num)]
        new_query = urlencode(qs, doseq=True)
        new_parsed = parsed._replace(query=new_query)
        return urlunparse(new_parsed)
    else:
        sep = "&" if "?" in template else "?"
        return f"{template}{sep}page={page_num}"


class WebDriverController:
    """Controller for WebDriver initialization and management."""
    
    def __init__(self):
        self.driver = None
        self.setup_driver()
    
    def setup_driver(self):
        """Setup or reset the web driver."""
        if self.driver:
            try:
                self.driver.quit()
            except Exception:
                pass
        
        options = Options()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Uncomment to run without GUI:
        # options.add_argument("--headless=new")
        
        try:
            self.driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()), 
                options=options
            )
            self.driver.execute_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            )
        except Exception as e:
            logging.error(f"Error setting up driver: {e}")
            raise

    def close(self):
        """Close the browser session."""
        logging.info("Closing browser...")
        try:
            if self.driver:
                self.driver.quit()
        except Exception as e:
            logging.warning(f"Error closing browser: {e}")


class PropertyListScraper:
    """Scraper for property listing pages."""
    
    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver

    def extract_links_and_prices(self) -> List[Dict]:
        """Extract property URLs, titles, and prices from listing pages."""
        time.sleep(1.0)
        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        properties = []

        # Specific selectors for the target website
        cards = soup.select(
            "div.property-item, div.listing-card, div.item, "
            "div.card, div.property, .list-item"
        )
        
        for card in cards:
            # Find links in different ways
            link_tag = (
                card.select_one("a[href*='bogotarealestate.com.co']") or 
                card.select_one("a.property-link") or
                card.select_one("a[href*='/apartamento']") or
                card.select_one("a[href*='/casa']")
            )
            
            if not link_tag:
                continue

            href = link_tag.get("href", "").strip()
            if not href:
                continue
                
            if href.startswith("/"):
                base = (
                    f"{urlparse(self.driver.current_url).scheme}://"
                    f"{urlparse(self.driver.current_url).netloc}"
                )
                href = base + href

            # Extract title
            title = "N/A"
            title_tag = (
                card.select_one("h2 a, h3 a, .title a, .property-title, .t8-ellipsis") or
                card.select_one("h2, h3, .title")
            )
            if title_tag:
                title = title_tag.get_text(strip=True)
            else:
                # Fallback: use link text
                title = link_tag.get_text(strip=True)
                if not title or len(title) < 5:
                    title = card.get_text(" ", strip=True)[:80]

            # Extract price
            price = "N/A"
            price_selectors = [
                ".price", ".precio", ".property-price", ".price_sale", 
                "[class*='price']", ".value", ".cost"
            ]
            for selector in price_selectors:
                price_tag = card.select_one(selector)
                if price_tag:
                    price_text = price_tag.get_text(strip=True)
                    if any(char.isdigit() for char in price_text):
                        price = price_text
                        break

            properties.append({
                "URL": href, 
                "Title": title, 
                "Price": price
            })

        logging.info(f"Found {len(properties)} properties on this page")
        return properties


class PropertyDetailScraper:
    """Scraper for property detail pages."""
    
    FIELD_MAP = {
        "país": "Country",
        "pais": "Country",
        "departamento": "State",
        "ciudad": "City",
        "localidad": "Locality",
        "zona / barrio": "Neighborhood",
        "zona": "Neighborhood",
        "barrio": "Neighborhood",
        "estado": "Status",
        "área construida": "Built Area",
        "area construida": "Built Area",
        "área terreno": "Land Area",
        "area terreno": "Land Area",
        "alcobas": "Bedrooms",
        "alcoba": "Bedrooms",
        "habitación": "Bedrooms",
        "habitaciones": "Bedrooms",
        "baño": "Bathrooms",
        "baños": "Bathrooms",
        "bano": "Bathrooms",
        "banos": "Bathrooms",
        "garaje": "Garage",
        "garajes": "Garage",
        "estrato": "Stratum",
        "piso": "Floor",
        "año construcción": "Year Built",
        "ano construccion": "Year Built",
        "tipo de inmueble": "Property Type",
        "tipo de negocio": "Business Type",
        "valor administración": "Administration Fee",
        "valor administracion": "Administration Fee"
    }

    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver
        self.normalized_map = {
            normalize_text(k): v for k, v in self.FIELD_MAP.items()
        }

    def _match_label(self, label_text: str) -> str:
        """Match Spanish labels to English field names."""
        key = normalize_text(label_text)
        if key in self.normalized_map:
            return self.normalized_map[key]
        for k_norm, v in self.normalized_map.items():
            if k_norm in key or key in k_norm:
                return v
        return None

    def extract_detail(self, url: str, title: str, price: str) -> Dict:
        """Extract detailed information from property page."""
        logging.info(f"Opening detail page: {url}")
        
        # Initialize item with default values
        item = {v: "N/A" for v in set(self.normalized_map.values())}
        item.update({
            "URL": url,
            "Title": title,
            "Price": price,
            "Extraction Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "Error": None
        })

        for attempt in range(MAX_RETRIES):
            try:
                self.driver.get(url)
                # Wait for relevant content to load
                WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                human_pause()
                break
            except Exception as e:
                logging.warning(f"Attempt {attempt + 1} failed for {url}: {e}")
                if attempt == MAX_RETRIES - 1:
                    item["Error"] = (
                        f"Failed to load after {MAX_RETRIES} attempts: {str(e)}"
                    )
                    return item
                time.sleep(2)

        soup = BeautifulSoup(self.driver.page_source, "html.parser")

        # Multiple extraction strategies
        extraction_methods = [
            self._extract_from_dl,
            self._extract_from_tables,
            self._extract_from_lists,
            self._extract_from_divs
        ]

        for method in extraction_methods:
            extracted_data = method(soup)
            if extracted_data:
                for key, value in extracted_data.items():
                    if value and value != "N/A":
                        item[key] = value

        return item

    def _extract_from_dl(self, soup: BeautifulSoup) -> Dict:
        """Extract data from definition lists (dl > dt + dd)."""
        data = {}
        for dl in soup.select("dl"):
            dts = dl.find_all("dt")
            for dt in dts:
                dd = dt.find_next_sibling("dd")
                if not dd:
                    continue
                label = dt.get_text(" ", strip=True).replace(":", "")
                val = dd.get_text(" ", strip=True)
                mapped = self._match_label(label)
                if mapped and val:
                    data[mapped] = val
                    logging.debug(f"Found {mapped}: {val} from dl")
        return data

    def _extract_from_tables(self, soup: BeautifulSoup) -> Dict:
        """Extract data from tables."""
        data = {}
        for table in soup.select("table"):
            rows = table.select("tr")
            for row in rows:
                cells = row.select("td, th")
                if len(cells) >= 2:
                    label = cells[0].get_text(" ", strip=True).replace(":", "")
                    val = cells[1].get_text(" ", strip=True)
                    mapped = self._match_label(label)
                    if mapped and val:
                        data[mapped] = val
                        logging.debug(f"Found {mapped}: {val} from table")
        return data

    def _extract_from_lists(self, soup: BeautifulSoup) -> Dict:
        """Extract data from unordered/ordered lists."""
        data = {}
        for ul in soup.select("ul"):
            items = ul.select("li")
            for item in items:
                text = item.get_text(" ", strip=True)
                # Look for patterns like "Habitaciones: 3"
                if ":" in text:
                    parts = text.split(":", 1)
                    if len(parts) == 2:
                        label = parts[0].strip()
                        val = parts[1].strip()
                        mapped = self._match_label(label)
                        if mapped and val:
                            data[mapped] = val
                            logging.debug(f"Found {mapped}: {val} from list")
        return data

    def _extract_from_divs(self, soup: BeautifulSoup) -> Dict:
        """Extract data from divs with common class patterns."""
        data = {}
        # Look for divs that might contain property information
        property_divs = soup.select(
            "div.property-info, div.details, div.characteristics"
        )
        for div in property_divs:
            text = div.get_text(" ", strip=True)
            # Look for common patterns
            patterns = {
                "Bedrooms": r"(\d+)\s*(?:alcoba|habitación|habitaciones|bedroom|bed)",
                "Bathrooms": r"(\d+)\s*(?:baño|baños|bathroom|bath)",
                "Garage": r"(\d+)\s*(?:garaje|garajes|garage|parking)"
            }
            
            import re
            for field, pattern in patterns.items():
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    data[field] = match.group(1)
                    logging.debug(f"Found {field}: {match.group(1)} from div pattern")
        
        return data


class PropertyExporter:
    """Handles data export to various formats."""
    
    @staticmethod
    def ensure_folder_exists():
        """Create data folder if it doesn't exist."""
        if not os.path.exists(DATA_FOLDER):
            os.makedirs(DATA_FOLDER)
            logging.info(f"Folder created: {DATA_FOLDER}")

    @staticmethod
    def save_files(sales_data: List[Dict], rentals_data: List[Dict]):
        """Save only CSV files: sales, rentals, and combined."""
        PropertyExporter.ensure_folder_exists()
        
        # Save sales data
        if sales_data:
            sales_df = pd.DataFrame(sales_data)
            sales_path = os.path.join(DATA_FOLDER, "properties_sales.csv")
            sales_df.to_csv(sales_path, index=False, encoding="utf-8-sig")
            logging.info(f"Saved {len(sales_data)} sales properties to {sales_path}")
        
        # Save rentals data
        if rentals_data:
            rentals_df = pd.DataFrame(rentals_data)
            rentals_path = os.path.join(DATA_FOLDER, "properties_rentals.csv")
            rentals_df.to_csv(rentals_path, index=False, encoding="utf-8-sig")
            logging.info(f"Saved {len(rentals_data)} rental properties to {rentals_path}")
        
        # Save combined data
        all_data = sales_data + rentals_data
        if all_data:
            all_df = pd.DataFrame(all_data)
            all_path = os.path.join(DATA_FOLDER, "properties_all.csv")
            all_df.to_csv(all_path, index=False, encoding="utf-8-sig")
            logging.info(f"Saved {len(all_data)} total properties to {all_path}")

    @staticmethod
    def save_json(data: List[Dict], filename: str):
        """Save data as JSON file."""
        PropertyExporter.ensure_folder_exists()
        path = os.path.join(DATA_FOLDER, filename)
        import json
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        logging.info(f"JSON saved: {path}")


class RealEstateScraper(Scraper):
    """
    Real estate scraper that inherits from Scraper base class.
    Uses Selenium for dynamic content scraping.
    """

    def __init__(self, save_every: int = SAVE_BATCH):
        # Initialize parent with empty endpoints since we use Selenium
        super().__init__(
            base_url="https://bogotarealestate.com.co", 
            endpoints=[]
        )
        self.ctrl = WebDriverController()
        self.list_scraper = PropertyListScraper(self.ctrl.driver)
        self.detail_scraper = PropertyDetailScraper(self.ctrl.driver)
        self.save_every = save_every
        self.sales_data = []
        self.rentals_data = []
        self.processed_urls = set()

    def parse(self, html):
        """
        Implement abstract method from parent class.
        Not used in Selenium approach but required by base class.
        """
        return []

    def fetch_html(self, endpoint):
        """
        Override parent method to use Selenium instead of requests.
        """
        url = self.base_url + endpoint
        try:
            self.ctrl.driver.get(url)
            WebDriverWait(self.ctrl.driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            human_pause()
            return self.ctrl.driver.page_source
        except Exception as error:
            logging.error(f"Request failed for {url}: {error}")
            return ""

    def run(self):
        """
        Override base run method using Selenium logic.
        This is the main scraping orchestration method.
        """
        try:
            sections = {
                "Sales": (
                    "https://bogotarealestate.com.co/search"
                    "?business_type%5B0%5D=for_sale&order_by=created_at"
                ),
                "Rentals": (
                    "https://bogotarealestate.com.co/search"
                    "?business_type%5B0%5D=for_rent&order_by=created_at"
                )
            }

            for section, template in sections.items():
                logging.info(f"Starting section: {section}")
                page = 1
                section_new_properties = []
                
                while page <= MAX_PAGES:
                    page_url = build_page_url_from_template(template, page)
                    logging.info(f"Loading page {page}: {page_url}")
                    
                    try:
                        self.ctrl.driver.get(page_url)
                        WebDriverWait(self.ctrl.driver, 15).until(
                            EC.presence_of_element_located((By.TAG_NAME, "body"))
                        )
                        human_pause()
                    except Exception as e:
                        logging.error(f"Error loading {page_url}: {e}")
                        break

                    props = self.list_scraper.extract_links_and_prices()
                    if not props:
                        logging.info(f"No properties found on page {page}, ending section")
                        break

                    logging.info(f"Processing {len(props)} properties from page {page}")
                    
                    for i, prop in enumerate(props):
                        # Skip if URL already processed
                        if prop["URL"] in self.processed_urls:
                            logging.info(f"Skipping duplicate: {prop['Title'][:50]}...")
                            continue
                            
                        logging.info(f"Processing: {prop['Title'][:50]}...")
                        
                        detail = self.detail_scraper.extract_detail(
                            prop["URL"], prop["Title"], prop["Price"]
                        )
                        detail["Section"] = section
                        
                        self.processed_urls.add(prop["URL"])
                        section_new_properties.append(detail)
                        
                        # Add to appropriate list
                        if section == "Sales":
                            self.sales_data.append(detail)
                        else:
                            self.rentals_data.append(detail)

                    # Log progress but don't save intermediate files
                    logging.info(
                        f"Section {section} progress: "
                        f"{len(section_new_properties)} new properties on page {page}"
                    )

                    page += 1

                logging.info(
                    f"Completed {section} section: {len(section_new_properties)} new properties"
                )

            # Final export - only CSV files and JSON
            logging.info("Saving final data files...")
            PropertyExporter.save_files(self.sales_data, self.rentals_data)
            PropertyExporter.save_json(
                self.sales_data + self.rentals_data, 
                "properties_all.json"
            )
            
            # Store data in parent class for compatibility
            self.data = self.sales_data + self.rentals_data
            
            logging.info(
                f"Scraping completed. "
                f"Sales: {len(self.sales_data)}, "
                f"Rentals: {len(self.rentals_data)}, "
                f"Total: {len(self.data)}"
            )

        except Exception as e:
            logging.error(f"Critical error in scraper: {e}")
            # Try to save collected data
            if self.sales_data or self.rentals_data:
                PropertyExporter.save_files(self.sales_data, self.rentals_data)
                logging.info(
                    f"Saved partial data: "
                    f"{len(self.sales_data)} sales, "
                    f"{len(self.rentals_data)} rentals"
                )
            raise
        finally:
            self.ctrl.close()

    def save_data(self, filename=None, folder=DATA_FOLDER):
        """
        Override parent save method to use our custom exporter.
        """
        if not self.data:
            logging.warning("No data to save.")
            return
        
        # Use our custom exporter for consistent file structure
        PropertyExporter.save_files(self.sales_data, self.rentals_data)
        PropertyExporter.save_json(self.data, "properties_all.json")


if __name__ == "__main__":
    logging.info("Starting RealEstateScraper test run...")
    scraper = RealEstateScraper(save_every=SAVE_BATCH)
    scraper.run()

