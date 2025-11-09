import os
import time
import json
import pandas as pd
from tqdm import tqdm
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from scraper_base import Scraper  # abstract base class


class RealEstateScraper(Scraper):
    def __init__(self, base_url, endpoints):
        super().__init__(base_url, endpoints)
        self.driver = None
        self.properties = {"sales": [], "rentals": []}

    # Initialize Selenium
    def _init_driver(self, visible=True):
        chrome_options = Options()
        if not visible:
            chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)

    # Load and return HTML
    def fetch_html(self, url):
        try:
            self.driver.get(url)
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.item"))
            )
            return self.driver.page_source
        except Exception:
            print(f"⚠️ Elements did not fully load at {url}")
            return self.driver.page_source

    # Parse property details page
    def parse_property_details(self, url):
        try:
            time.sleep(1.5)
            self.driver.get(url)
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "ul.list-li"))
            )
            html = self.driver.page_source
            soup = BeautifulSoup(html, "html.parser")
            details = soup.select("ul.list-li li")
            data = {}
            for li in details:
                key_el = li.find("strong")
                if key_el:
                    key = key_el.get_text(strip=True).replace(":", "")
                    value = key_el.next_sibling.strip() if key_el.next_sibling else ""
                    data[key] = value

            fields = [
                "País", "Departamento", "Ciudad", "Localidad", "Zona / barrio",
                "Estado", "Área Terreno", "Baño", "Estrato",
                "Tipo de inmueble", "Tipo de negocio"
            ]

            clean_data = {f: data.get(f, "") for f in fields}
            # Translate keys to English
            translated = {
                "Country": clean_data["País"],
                "Department": clean_data["Departamento"],
                "City": clean_data["Ciudad"],
                "District": clean_data["Localidad"],
                "Neighborhood": clean_data["Zona / barrio"],
                "Condition": clean_data["Estado"],
                "Land Area": clean_data["Área Terreno"],
                "Bathrooms": clean_data["Baño"],
                "Stratum": clean_data["Estrato"],
                "Property Type": clean_data["Tipo de inmueble"],
                "Business Type": clean_data["Tipo de negocio"],
            }
            return translated

        except Exception as e:
            print(f"⚠️ Error reading property details at {url}: {e}")
            return {}

    # Parse main listing page
    def parse(self, html):
        soup = BeautifulSoup(html, "html.parser")
        cards = soup.select("div.item, div.list-property .item")

        properties = []
        for card in tqdm(cards, desc="🔍 Parsing properties", leave=False):
            try:
                title_el = card.select_one("h2 a")
                price_el = card.select_one(".precio")
                url = title_el["href"].strip() if title_el and title_el.has_attr("href") else None

                if not url:
                    continue

                details = self.parse_property_details(url)
                details["Title"] = title_el.get_text(strip=True) if title_el else ""
                details["Price"] = price_el.get_text(strip=True) if price_el else ""
                details["URL"] = url
                properties.append(details)

                # Restart driver every 10 requests to avoid memory issues
                if len(properties) % 10 == 0:
                    self.driver.quit()
                    self._init_driver(visible=False)

            except Exception as e:
                print(f"⚠️ Error processing property card: {e}")
                continue

        print(f"✅ Page parsed: {len(properties)} properties found.")
        return properties

    # Full scraper execution
    def run(self):
        self._init_driver(visible=True)
        try:
            for endpoint in self.endpoints:
                prop_type = "sales" if "for_sale" in endpoint else "rentals"
                page = 1
                all_props = []

                while True:
                    url = endpoint.replace("_n_", str(page))
                    print(f"\n📄 Extracting page {page}: {url}")
                    html = self.fetch_html(url)
                    props = self.parse(html)

                    if not props:
                        print("✅ No more properties found.")
                        break

                    all_props.extend(props)
                    page += 1
                    time.sleep(2)

                # Save separate CSVs
                df = pd.DataFrame(all_props).drop_duplicates(subset=["Title", "Price"])
                file = f"properties_{prop_type}.csv"
                df.to_csv(file, index=False, encoding="utf-8-sig")
                print(f"💾 File saved: {file} ({len(df)} properties)")

                self.properties[prop_type] = df

            # Combine both into single CSV + Excel
            self.combine_files()

        finally:
            self.driver.quit()
            print("🚪 Browser closed.")

    # Combine all into single file
    def combine_files(self):
        try:
            df_sales = self.properties["sales"]
            df_rentals = self.properties["rentals"]

            if df_sales.empty and df_rentals.empty:
                print("⚠️ No data to combine.")
                return

            combined = pd.concat([df_sales, df_rentals], ignore_index=True)
            combined.to_csv("properties_combined.csv", index=False, encoding="utf-8-sig")
            combined.to_excel("properties_combined.xlsx", index=False)
            print("📊 Combined files created: properties_combined.csv and properties_combined.xlsx")

        except Exception as e:
            print(f"❌ Error combining files: {e}")


# ---------------------------
# 🚀 MAIN EXECUTION
# ---------------------------
if __name__ == "__main__":
    BASE_URL = "https://bogotarealestate.com.co"
    ENDPOINTS = [
        "https://bogotarealestate.com.co/search?business_type%5B0%5D=for_sale&order_by=created_at&order=desc&page=_n_&for_sale=1&for_rent=0&for_temporary_rent=0&for_transfer=0&lax_business_type=1",
        "https://bogotarealestate.com.co/search?business_type%5B0%5D=for_rent&order_by=created_at&order=desc&page=_n_&for_sale=0&for_rent=1&for_temporary_rent=0&for_transfer=0&lax_business_type=1",
    ]

    scraper = RealEstateScraper(BASE_URL, ENDPOINTS)
    scraper.run()
