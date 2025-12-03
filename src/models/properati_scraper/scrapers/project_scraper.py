"""
Project scraper for handling property projects with multiple units.
"""

import logging
from datetime import datetime
from urllib.parse import urljoin
from bs4 import BeautifulSoup

from src.models.properati_scraper.scrapers.base_scraper import SeleniumBaseScraper
from src.models.properati_scraper.utils.helpers import (
    safe_extract,
    extract_numeric_value,
    extract_business_type,
)
from ..config import (
    BASE_URL,
    BEDROOM_KEYWORDS,
    BATHROOM_KEYWORDS,
    GARAGE_KEYWORDS,
    LOT_KEYWORDS,
)


class ProjectScraper(SeleniumBaseScraper):
    """Scraper for property projects with multiple units."""

    def __init__(self, driver):
        super().__init__(driver)

    def extract_unit_links(self, project_url):
        """
        Extract links to individual units from project page.

        Args:
            project_url: Project page URL

        Returns:
            List of unit URLs
        """
        logging.info(f"Extracting units from project: {project_url}")

        html = self.scrape_with_captcha_protection(project_url)
        if html is None:
            return []

        soup = BeautifulSoup(html, "html.parser")
        unit_links = []

        # Search for unit links in different sections
        selectors = [
            "a[href*='/detalle/']",
            ".similar-snippet a",
            ".unit-card a",
            ".listing-card a",
            "[data-test*='property-card'] a",
        ]

        for selector in selectors:
            links = soup.select(selector)
            for link in links:
                href = link.get("href")
                if href and "/detalle/" in href:
                    full_url = urljoin(BASE_URL, href)
                    if full_url not in unit_links:
                        unit_links.append(full_url)

        # If no direct units found, search in "Available Units" sections
        if not unit_links:
            unit_sections = soup.select(
                ".units-section, .available-units, .project-units"
            )
            for section in unit_sections:
                section_links = section.select("a[href*='/detalle/']")
                for link in section_links:
                    href = link.get("href")
                    if href:
                        full_url = urljoin(BASE_URL, href)
                        if full_url not in unit_links:
                            unit_links.append(full_url)

        logging.info(f"Project has {len(unit_links)} individual units")
        return unit_links

    def _extract_project_details(self, soup):
        """
        Extract specific project details.

        Args:
            soup: BeautifulSoup object

        Returns:
            Dictionary with project details
        """
        details = {}
        details_items = soup.select(".units-summary .details-item__text")

        for detail in details_items:
            text = detail.get_text(strip=True)
            text_lower = text.lower()

            if "unidades" in text_lower:
                details["units"] = text
            elif "habitaciones" in text_lower:
                details["bedrooms"] = text
            elif "baños" in text_lower:
                details["bathrooms"] = text
            elif "área construida" in text_lower:
                details["built_area"] = text
            elif "área total" in text_lower:
                details["land_area"] = text

        return details

    def _extract_project_info(self, soup, project_url):
        """
        Extract general project information.

        Args:
            soup: BeautifulSoup object
            project_url: Project URL

        Returns:
            Dictionary with project information
        """
        project_details = self._extract_project_details(soup)

        item = {
            "URL": project_url,
            "Title": safe_extract(soup, ["h1.header__text", "h1.title"]),
            "Neighborhood": safe_extract(soup, [".header__location span", ".location"]),
            "Price": safe_extract(soup, [".price-info__value", ".price"]),
            "Built Area": project_details.get("built_area", "N/A"),
            "Land Area": project_details.get("land_area", "N/A"),
            "Bedrooms": project_details.get("bedrooms", "N/A"),
            "Bathrooms": project_details.get("bathrooms", "N/A"),
            "Garage": "N/A",
            "Stratum": "N/A",
            "Year Built": "N/A",
            "Administration Fee": "N/A",
            "Property Type": "Proyecto",
            "Business Type": extract_business_type(project_url, soup),
            "Status": "N/A",
            "Extraction Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "Error": None,
            "Project_Units": project_details.get("units", "N/A"),
            "Is_Project": "Sí",
            "Price_Label": safe_extract(soup, [".price-info__from"], "Precio"),
            "Has_Individual_Units": "Sí" if project_details.get("units") else "No",
        }

        return item

    def scrape_unit_property(self, unit_url):
        """
        Scrape individual unit from project.

        Args:
            unit_url: Unit property URL

        Returns:
            Dictionary with unit data
        """
        try:
            logging.info(f"Scraping unit: {unit_url}")
            html = self.scrape_with_captcha_protection(unit_url)

            if html is None:
                return {
                    "URL": unit_url,
                    "Error": "CAPTCHA detected",
                    "Extraction Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                }

            soup = BeautifulSoup(html, "html.parser")

            # Use same extraction logic as DetailScraper
            property_type = safe_extract(
                soup,
                [
                    "[data-test='property-type-value']",
                    ".property-type .place-features__values",
                    ".property-type",
                ],
            ).lower()

            is_lot_or_land = any(word in property_type for word in LOT_KEYWORDS)

            item = {
                "URL": unit_url,
                "Title": safe_extract(
                    soup,
                    [".main-title h1", "h1.title", "[data-test='listing-title']", "h1"],
                ),
                "Neighborhood": safe_extract(
                    soup,
                    [
                        ".location",
                        "[data-test='location']",
                        ".property-location",
                        ".address",
                    ],
                ),
                "Price": safe_extract(
                    soup,
                    [
                        "[data-test='listing-price']",
                        ".prices-and-fees__price",
                        ".price",
                        ".listing-price",
                        ".value",
                    ],
                ),
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
                else extract_numeric_value(
                    soup, "full-bathrooms-value", BATHROOM_KEYWORDS
                ),
                "Garage": extract_numeric_value(
                    soup, "parking-lots-value", GARAGE_KEYWORDS
                ),
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
                "Business Type": extract_business_type(unit_url, soup),
                "Status": "N/A",
                "Extraction Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Error": None,
                "Property_Category": "Lote/Terreno"
                if is_lot_or_land
                else "Construcción",
            }

            return item

        except Exception as e:
            logging.error(f"Error scraping unit {unit_url}: {e}")
            return {
                "URL": unit_url,
                "Error": f"unit_scraping_error: {str(e)}",
                "Extraction Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            }

    def scrape_project_with_units(self, project_url):
        """
        Scrape complete project with all individual units.

        Args:
            project_url: Project page URL

        Returns:
            List of project and unit data dictionaries
        """
        project_data = []

        try:
            # 1. First scrape the main project page
            html = self.scrape_with_captcha_protection(project_url)
            if html is None:
                project_data.append(
                    {
                        "URL": project_url,
                        "Error": "CAPTCHA detected",
                        "Extraction Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    }
                )
                return project_data

            project_soup = BeautifulSoup(html, "html.parser")

            # 2. Extract general project information
            project_info = self._extract_project_info(project_soup, project_url)

            # 3. Extract links to individual units
            unit_links = self.extract_unit_links(project_url)

            # 4. Add main project record
            project_data.append(project_info)

            # 5. Scrape each individual unit
            for i, unit_url in enumerate(unit_links, 1):
                logging.info(f"Scraping unit {i}/{len(unit_links)}")

                # Scrape the individual unit
                unit_result = self.scrape_unit_property(unit_url)
                if unit_result and not unit_result.get("Error"):
                    # Mark as project unit
                    unit_result["Project_Parent"] = project_url
                    unit_result["Project_Name"] = project_info.get("Title", "N/A")
                    unit_result["Is_Project_Unit"] = "Sí"
                    project_data.append(unit_result)
                else:
                    logging.warning(f"Could not scrape unit: {unit_url}")

            logging.info(
                f"Project completed: {len(project_data)} records (1 project + {len(unit_links)} units)"
            )

        except Exception as e:
            logging.error(f"Error scraping project {project_url}: {e}")
            project_data.append(
                {
                    "URL": project_url,
                    "Title": "Error scraping project",
                    "Error": f"project_error: {str(e)}",
                    "Extraction Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                }
            )

        return project_data
