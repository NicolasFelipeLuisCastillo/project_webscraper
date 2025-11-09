import logging
from bs4 import BeautifulSoup
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re
from utils import normalize_text

MAX_RETRIES = 3

class PropertyDetailExtractor:
    """Extrae información detallada de cada propiedad."""

    FIELD_MAP = {
        "país": "Country", "pais": "Country",
        "departamento": "State", "ciudad": "City",
        "localidad": "Locality", "zona / barrio": "Neighborhood",
        "zona": "Neighborhood", "barrio": "Neighborhood",
        "estado": "Status", "área construida": "Built Area",
        "area construida": "Built Area", "área terreno": "Land Area",
        "area terreno": "Land Area", "alcobas": "Bedrooms",
        "alcoba": "Bedrooms", "habitación": "Bedrooms",
        "habitaciones": "Bedrooms", "baño": "Bathrooms",
        "baños": "Bathrooms", "bano": "Bathrooms", "banos": "Bathrooms",
        "garaje": "Garage", "garajes": "Garage", "estrato": "Stratum",
        "piso": "Floor", "año construcción": "Year Built",
        "ano construccion": "Year Built", "tipo de inmueble": "Property Type",
        "tipo de negocio": "Business Type", "valor administración": "Administration Fee",
        "valor administracion": "Administration Fee",
        "precio": "Price", "valor": "Price", "coste": "Price"
    }

    def __init__(self, ctrl):
        self.driver = ctrl.driver
        self.normalized_map = {normalize_text(k): v for k, v in self.FIELD_MAP.items()}

    def _match_label(self, label_text: str) -> str:
        key = normalize_text(label_text)
        if key in self.normalized_map:
            return self.normalized_map[key]
        for k_norm, v in self.normalized_map.items():
            if k_norm in key or key in k_norm:
                return v
        return None

    def _clean_value(self, value: str, field: str = None) -> str:
        """Limpia y normaliza los valores extraídos."""
        if not value or value == "N/A":
            return "N/A"
        
        value = value.strip()
        
        # Limpieza específica por campo
        if field == "Price":
            # Extraer solo números y puntos para precios
            match = re.search(r'[\$]?\s*([\d\.]+)\s*[\$]?', value)
            if match:
                return f"${match.group(1)}"
        
        elif field in ["Built Area", "Land Area"]:
            # Limpiar áreas, mantener solo números y m²
            match = re.search(r'([\d\.,]+)\s*m²', value)
            if match:
                cleaned = match.group(1).replace(',', '.').replace(' ', '')
                return f"{cleaned} m²"
        
        elif field == "Year Built":
            # Solo años de 4 dígitos
            match = re.search(r'(19|20)\d{2}', value)
            if match:
                return match.group(0)
        
        elif field in ["Bedrooms", "Bathrooms", "Garage", "Stratum", "Floor"]:
            # Solo números para campos numéricos
            match = re.search(r'(\d+)', value)
            if match:
                return match.group(1)
        
        return value

    def extract(self, url: str, title="", price="", section="Sales") -> dict:
        logging.info(f"Abriendo detalle: {url}")

        # Inicializa todas las columnas con "N/A"
        item = {v: "N/A" for v in set(self.normalized_map.values())}
        item.update({
            "URL": url,
            "Title": title or "N/A",
            "Price": price or "N/A",
            "Extraction Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "Error": None,
            "Section": section
        })

        # Si ya tenemos precio del listado, intentar limpiarlo
        if price and price != "N/A":
            item["Price"] = self._clean_value(price, "Price")

        # Intentos de carga
        for attempt in range(MAX_RETRIES):
            try:
                self.driver.get(url)
                WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                time.sleep(2)
                break
            except Exception as e:
                logging.warning(f"Intento {attempt+1} fallido: {e}")
                if attempt == MAX_RETRIES - 1:
                    item["Error"] = f"No se pudo cargar la página: {e}"
                    return item

        soup = BeautifulSoup(self.driver.page_source, "html.parser")

        # Extraer precio de la página de detalle (sobrescribe el del listado si es mejor)
        detail_price = self._extract_price(soup)
        if detail_price and detail_price != "N/A":
            item["Price"] = detail_price

        # Extracción completa usando todos los métodos
        for method in [self._extract_from_dl, self._extract_from_tables,
                       self._extract_from_lists, self._extract_from_divs,
                       self._extract_from_spans]:
            extracted_data = method(soup)
            for k, v in extracted_data.items():
                if v and v != "N/A":
                    item[k] = v

        return item

    def _extract_price(self, soup: BeautifulSoup) -> str:
        """Extrae el precio de la página de detalle."""
        price_selectors = [
            ".price", ".precio", ".property-price", 
            "[class*='price']", "[class*='precio']",
            "h1 .price", "h2 .price", "h3 .price",
            ".value", ".cost", ".valor"
        ]
        
        for selector in price_selectors:
            elements = soup.select(selector)
            for element in elements:
                text = element.get_text(strip=True)
                if any(char.isdigit() for char in text):
                    cleaned = self._clean_value(text, "Price")
                    if cleaned != "N/A":
                        return cleaned
        
        return "N/A"

    def _extract_from_dl(self, soup: BeautifulSoup) -> dict:
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
                    data[mapped] = self._clean_value(val, mapped)
        return data

    def _extract_from_tables(self, soup: BeautifulSoup) -> dict:
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
                        data[mapped] = self._clean_value(val, mapped)
        return data

    def _extract_from_lists(self, soup: BeautifulSoup) -> dict:
        data = {}
        for ul in soup.select("ul"):
            for li in ul.select("li"):
                text = li.get_text(" ", strip=True)
                if ":" in text:
                    parts = text.split(":", 1)
                    if len(parts) == 2:
                        label, val = parts[0].strip(), parts[1].strip()
                        mapped = self._match_label(label)
                        if mapped and val:
                            data[mapped] = self._clean_value(val, mapped)
        return data

    def _extract_from_divs(self, soup: BeautifulSoup) -> dict:
        data = {}
        # Buscar en divs con clases comunes de propiedades
        for div in soup.select("div.property-info, div.details, div.characteristics, div.features"):
            text = div.get_text(" ", strip=True)
            
            # Patrones mejorados para extracción
            patterns = {
                "Bedrooms": r'(\d+)\s*(?:alcoba|habitación|habitaciones|dormitorio|bedroom|bed|hab)',
                "Bathrooms": r'(\d+)\s*(?:baño|baños|bano|banos|bathroom|bath)',
                "Garage": r'(\d+)\s*(?:garaje|garajes|garage|parking|parqueadero)',
                "Stratum": r'(?:estrato|stratum)\s*(\d+)',
                "Floor": r'(?:piso|floor)\s*(\d+)',
                "Built Area": r'(\d+(?:[.,]\d+)?)\s*m²\s*(?:construid|área construida|area construida)',
                "Land Area": r'(\d+(?:[.,]\d+)?)\s*m²\s*(?:terreno|área terreno|area terreno)'
            }
            
            for field, pattern in patterns.items():
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    data[field] = self._clean_value(match.group(1), field)
        
        return data

    def _extract_from_spans(self, soup: BeautifulSoup) -> dict:
        """Extrae información de elementos span que suelen contener datos de propiedades."""
        data = {}
        
        # Buscar spans que contengan iconos o etiquetas comunes
        icon_patterns = {
            "bed": "Bedrooms",
            "bath": "Bathrooms", 
            "car": "Garage",
            "area": "Built Area",
            "terrain": "Land Area"
        }
        
        for span in soup.select("span"):
            text = span.get_text(strip=True)
            class_attr = span.get("class", [])
            class_str = " ".join(class_attr).lower()
            
            # Buscar por contenido de clases
            for pattern, field in icon_patterns.items():
                if pattern in class_str and text:
                    cleaned = self._clean_value(text, field)
                    if cleaned != "N/A":
                        data[field] = cleaned
        
        return data