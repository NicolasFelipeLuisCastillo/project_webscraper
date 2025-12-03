"""
Detail page scraper for individual properties.
"""

import logging
import re
from datetime import datetime
from bs4 import BeautifulSoup

from src.models.properati_scraper.scrapers.base_scraper import SeleniumBaseScraper
from src.models.properati_scraper.utils.helpers import (
    safe_extract,
    extract_numeric_value,
    extract_business_type,
)
from ..config import (
    TITLE_SELECTORS,
    PRICE_SELECTORS,
    LOCATION_SELECTORS,
    BEDROOM_KEYWORDS,
    BATHROOM_KEYWORDS,
    LOT_KEYWORDS,
)


class DetailScraper(SeleniumBaseScraper):
    """Scraper for individual property detail pages."""

    def __init__(self, driver):
        super().__init__(driver)

    def _extract_garage_specific(self, soup):
        """
        Extract garage count specifically, avoiding confusion with area values.

        Args:
            soup: BeautifulSoup object

        Returns:
            Garage count or "N/A"
        """
        # 1. First try data-test attribute (most reliable)
        elements = soup.select('[data-test="parking-lots-value"]')
        for element in elements:
            text = element.get_text(strip=True)
            numbers = re.findall(r"\d+", text)
            if numbers:
                return numbers[0]

        # 2. Look for garage-specific elements with icons
        garage_icons = soup.select(
            '.details-item__icon-parking, .details-item__icon-garage, [alt*="parking"], [alt*="garage"]'
        )
        for icon in garage_icons:
            # Find the parent details-item and then the value
            details_item = icon.find_parent("div", class_="details-item")
            if details_item:
                value_element = details_item.select_one(".details-item-value")
                if value_element:
                    text = value_element.get_text(strip=True)
                    numbers = re.findall(r"\d+", text)
                    if numbers:
                        return numbers[0]

        # 3. Look for text containing garage keywords but NOT area keywords
        garage_keywords = ["garaje", "estacionamiento", "parqueadero", "parking"]
        area_keywords = ["m²", "m2", "metro", "área", "area"]

        all_elements = soup.find_all(
            class_=re.compile("details-item-value|value|facilities__item")
        )
        for element in all_elements:
            text = element.get_text(strip=True).lower()
            # Check if it contains garage keywords but NOT area keywords
            if any(keyword in text for keyword in garage_keywords) and not any(
                keyword in text for keyword in area_keywords
            ):
                numbers = re.findall(r"\d+", text)
                if numbers:
                    return numbers[0]

        # 4. Check facilities section for parking
        facilities_items = soup.select(".facilities__item")
        for item in facilities_items:
            text = item.get_text(strip=True).lower()
            if any(keyword in text for keyword in garage_keywords):
                # If it's just listed as a facility without number, assume 1
                return "1"

        return "N/A"

    def _extract_description(self, soup):
        """
        Extract property description.

        Args:
            soup: BeautifulSoup object

        Returns:
            Description text or "N/A"
        """
        description_selectors = [
            ".description .content",
            "#description-text",
            ".property-description",
            "[data-test='description']",
        ]

        for selector in description_selectors:
            element = soup.select_one(selector)
            if element:
                text = element.get_text(strip=True)
                if text and text not in ["", "-"]:
                    # Clean up the text - remove extra whitespace but preserve paragraphs
                    text = re.sub(r"\s+", " ", text)
                    return text[:5000] if len(text) > 5000 else text

        return "N/A"

    def _extract_features(self, soup):
        """
        Extract property features/amenities.

        Args:
            soup: BeautifulSoup object

        Returns:
            List of features or ["N/A"]
        """
        features = []

        # Extract from facilities section
        facilities_items = soup.select(".facilities__item span")
        for item in facilities_items:
            text = item.get_text(strip=True)
            if text and text not in ["", "-"]:
                features.append(text)

        # Also look for features in other common sections
        feature_sections = soup.select(
            ".features-list li, .amenities li, .characteristics li"
        )
        for item in feature_sections:
            text = item.get_text(strip=True)
            if text and text not in ["", "-"] and text not in features:
                features.append(text)

        return features if features else ["N/A"]

    def _extract_half_bathrooms(self, soup):
        """
        Extract half bathrooms count.

        Args:
            soup: BeautifulSoup object

        Returns:
            Half bathrooms count or "N/A"
        """
        # Look for half bathroom elements
        half_bath_selectors = [
            '[data-test="half-bathrooms-value"]',
            ".details-item__icon-halfBathroom + .details-item-value",
            '.details-item-value:contains("Medio baño")',
            '.details-item-value:contains("medio baño")',
        ]

        for selector in half_bath_selectors:
            elements = soup.select(selector)
            for element in elements:
                text = element.get_text(strip=True)
                numbers = re.findall(r"\d+", text)
                if numbers:
                    return numbers[0]

        return "N/A"

    def _extract_floor_level(self, soup):
        """
        Extract floor level.

        Args:
            soup: BeautifulSoup object

        Returns:
            Floor level or "N/A"
        """
        return safe_extract(
            soup,
            [
                '[data-test="floor-value"]',
                ".floor .place-features__values",
                '[class*="floor"] .value',
            ],
        )

    def _parse_detalle_html(self, html, url):
        """
        Parse individual property detail page.

        Args:
            html: Page HTML content
            url: Property URL

        Returns:
            Dictionary with property data
        """
        soup = BeautifulSoup(html, "html.parser")

        # Detect property type
        property_type = safe_extract(
            soup,
            [
                "[data-test='property-type-value']",
                ".property-type .place-features__values",
                ".property-type",
            ],
        ).lower()

        # For lots and land, don't look for bedrooms/bathrooms
        is_lot_or_land = any(word in property_type for word in LOT_KEYWORDS)

        # Extract features and description
        features = self._extract_features(soup)
        description = self._extract_description(soup)

        item = {
            "URL": url,
            "Title": safe_extract(soup, TITLE_SELECTORS),
            "Neighborhood": safe_extract(soup, LOCATION_SELECTORS),
            "Price": safe_extract(soup, PRICE_SELECTORS),
            "Built Area": safe_extract(
                soup,
                [
                    "[data-test='floor-area-value']",
                    ".floor-area .place-features__values",
                    ".built-area",
                    "[class*='area']",
                ],
            ),
            "Land Area": safe_extract(
                soup,
                [
                    "[data-test='plot-area-value']",
                    "[data-test='area-value']",
                    ".plot-area .place-features__values",
                    ".land-area",
                    ".area-land",
                ],
            ),
            "Bedrooms": "N/A"
            if is_lot_or_land
            else extract_numeric_value(soup, "bedrooms-value", BEDROOM_KEYWORDS),
            "Bathrooms": "N/A"
            if is_lot_or_land
            else extract_numeric_value(soup, "full-bathrooms-value", BATHROOM_KEYWORDS),
            "Half Bathrooms": "N/A"
            if is_lot_or_land
            else self._extract_half_bathrooms(soup),
            "Garage": self._extract_garage_specific(soup),
            "Stratum": safe_extract(
                soup,
                [
                    "[data-test='stratum-value']",
                    ".stratum .place-features__values",
                    ".stratum",
                    "[class*='stratum']",
                ],
            ),
            "Year Built": safe_extract(
                soup,
                [
                    "[data-test='construction-year-value']",
                    ".year .place-features__values",
                    ".year-built",
                    ".construction-year",
                    "[class*='year']",
                ],
            ),
            "Floor Level": self._extract_floor_level(soup),
            "Administration Fee": safe_extract(
                soup,
                [
                    "[data-test='community-price']",
                    ".administration",
                    ".admin-fee",
                    "[class*='admin']",
                ],
            ),
            "Property Type": safe_extract(
                soup,
                [
                    "[data-test='property-type-value']",
                    ".property-type .place-features__values",
                    ".property-type",
                    "[class*='type']",
                ],
            ),
            "Business Type": extract_business_type(url, soup),
            "Status": "N/A",
            "Extraction Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "Error": None,
            "Property_Category": "Lote/Terreno" if is_lot_or_land else "Construcción",
            "Description": description,
            "Features": ", ".join(features) if features != ["N/A"] else "N/A",
            "Features_Count": len(features) if features != ["N/A"] else "0",
        }

        return item

    def _parse_proyecto_html(self, html, url):
        """
        Parse project page (basic info).

        Args:
            html: Page HTML content
            url: Project URL

        Returns:
            Dictionary with project data
        """
        soup = BeautifulSoup(html, "html.parser")

        # Extract features and description for projects too
        features = self._extract_features(soup)
        description = self._extract_description(soup)

        item = {
            "URL": url,
            "Title": safe_extract(
                soup, ["h1.header__text", "h1.title", ".project-title", "h1"]
            ),
            "Neighborhood": safe_extract(
                soup,
                [
                    ".header__location span",
                    ".location",
                    ".project-location",
                    ".address",
                ],
            ),
            "Price": safe_extract(
                soup, [".price-info__value", ".price", ".project-price", ".value"]
            ),
            "Built Area": "N/A",
            "Land Area": "N/A",
            "Bedrooms": "N/A",
            "Bathrooms": "N/A",
            "Half Bathrooms": "N/A",
            "Garage": "N/A",
            "Stratum": "N/A",
            "Year Built": "N/A",
            "Floor Level": "N/A",
            "Administration Fee": "N/A",
            "Property Type": "Proyecto",
            "Business Type": extract_business_type(url, soup),
            "Status": "N/A",
            "Extraction Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "Error": None,
            "Is_Project": "Sí",
            "Description": description,
            "Features": ", ".join(features) if features != ["N/A"] else "N/A",
            "Features_Count": len(features) if features != ["N/A"] else "0",
        }

        return item

    def scrape_property(self, url):
        """
        Main method to scrape individual property.

        Args:
            url: Property URL

        Returns:
            Dictionary with property data
        """
        try:
            logging.info(f"Scraping property: {url}")
            html = self.scrape_with_captcha_protection(url)

            if html is None:
                return {
                    "URL": url,
                    "Error": "CAPTCHA detected",
                    "Extraction Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                }

            if "/proyecto/" in url:
                return self._parse_proyecto_html(html, url)
            elif "/detalle/" in url:
                return self._parse_detalle_html(html, url)
            else:
                return {"URL": url, "Error": "Unknown URL type"}

        except Exception as e:
            logging.error(f"Error scraping property {url}: {e}")
            return {
                "URL": url,
                "Error": f"scraping_error: {str(e)}",
                "Extraction Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            }
