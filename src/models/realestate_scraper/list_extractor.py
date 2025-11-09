import time
import random
import logging
from bs4 import BeautifulSoup
from typing import List, Dict

PAGE_LOAD_BASE = 3
RAND_DELAY = (0.5, 1.5)

def human_pause():
    time.sleep(PAGE_LOAD_BASE + random.uniform(*RAND_DELAY))

class PropertyListExtractor:
    """Extrae URLs y precios de la lista de propiedades."""

    def __init__(self, ctrl):
        self.driver = ctrl.driver

    def extract(self, url: str) -> List[Dict]:
        logging.info(f"Cargando página de listado: {url}")
        self.driver.get(url)
        human_pause()
        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        properties = []

        # Selectores más comprehensivos
        cards = soup.select(
            "div.property-item, div.listing-card, div.item, div.card, "
            "div.property, .list-item, .property-listing, .listing-item, "
            "[class*='property'], [class*='listing']"
        )

        for card in cards:
            # Buscar enlaces de manera más agresiva
            link_tag = (
                card.select_one("a[href*='bogotarealestate.com.co']") or 
                card.select_one("a.property-link") or
                card.select_one("a[href*='/apartamento']") or
                card.select_one("a[href*='/casa']") or
                card.select_one("a[href*='/inmueble']") or
                card.select_one("a[class*='link']") or
                card.select_one("h2 a, h3 a, h4 a") or
                card.select_one("a")
            )
            
            if not link_tag or not link_tag.get("href"):
                continue
                
            href = link_tag.get("href", "").strip()
            
            # Construir URL completa
            if href.startswith("/"):
                base = f"{self.driver.current_url.split('/')[0]}//{self.driver.current_url.split('/')[2]}"
                href = base + href
            elif href.startswith("http"):
                pass  # URL ya está completa
            else:
                # URL relativa sin slash
                base = "/".join(self.driver.current_url.split("/")[:-1])
                href = base + "/" + href

            # Extraer título
            title = "N/A"
            title_selectors = ["h2", "h3", "h4", ".title", ".property-title", ".name"]
            for selector in title_selectors:
                title_elem = card.select_one(selector)
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    break
            if title == "N/A" and link_tag:
                title = link_tag.get_text(strip=True)

            # Extraer precio mejorado
            price = "N/A"
            price_selectors = [".price", ".precio", ".property-price", ".value", ".cost"]
            for selector in price_selectors:
                price_elem = card.select_one(selector)
                if price_elem:
                    price_text = price_elem.get_text(strip=True)
                    if any(char.isdigit() for char in price_text):
                        price = price_text
                        break

            properties.append({
                "URL": href, 
                "Title": title, 
                "Price": price
            })

        logging.info(f"Se encontraron {len(properties)} propiedades en {url}")
        return properties