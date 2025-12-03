import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class SimpleListingScraper:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 20)

    def get_random_property_url(self, search_url):
        """Gets a random property URL from the search page"""
        print(f"Searching properties in COLOMBIA: {search_url}")
        self.driver.get(search_url)

        # Wait for page load
        time.sleep(random.uniform(5, 8))

        print("Page loaded, looking for properties in Colombia...")

        property_urls = []

        try:
            # Find all links that may be property links
            all_links = self.driver.find_elements(By.TAG_NAME, "a")
            print(f"Found {len(all_links)} links in total")

            for i, link in enumerate(all_links):
                try:
                    href = link.get_attribute("href")
                    if href and "properati.com.co" in href:
                        # Include only URLs that look like specific properties (with IDs or long slugs)
                        if ("/s/" in href or "/propiedad/" in href) and len(href) > 50:
                            # Exclude general category pages
                            if not any(
                                pattern in href
                                for pattern in [
                                    "/venta",
                                    "/alquiler",
                                    "?page=",
                                    "?operation=",
                                ]
                            ):
                                if href not in property_urls:
                                    property_urls.append(href)
                                    print(
                                        f"COLOMBIA property found ({len(property_urls)}): {href}"
                                    )
                except Exception:
                    continue

            print(f"Total COLOMBIA properties found: {len(property_urls)}")

            # If none found with strict filter, try more flexible search
            if not property_urls:
                print("🔍 Flexible property search...")
                for link in all_links:
                    try:
                        href = link.get_attribute("href")
                        if href and "properati.com.co" in href and "/s/" in href:
                            if href not in property_urls:
                                property_urls.append(href)
                                print(f"Property found (flexible): {href}")
                    except:
                        continue

            if property_urls:
                # Choose a random property
                selected_url = random.choice(property_urls)
                print(f"Selected COLOMBIA URL: {selected_url}")
                return selected_url
            else:
                print("No properties found in Colombia")
                return None

        except Exception as e:
            print(f"Error searching properties: {e}")
            return None


class SimpleDetailScraper:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 20)

    def scrape(self, url):
        print(f"Navigating to COLOMBIA property: {url}")
        self.driver.get(url)

        # Wait more intelligently
        time.sleep(random.uniform(4, 7))

        # Check if page loaded correctly
        if "properati.com.co" not in self.driver.current_url:
            return {"error": "Properati Colombia page did not load"}

        data = {}

        try:
            # Wait for content to load
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

            # Title - search in multiple places
            title_selectors = [
                "h1",
                ".posting-title",
                "[data-qa='posting-title']",
                ".title",
                "h1.title",
                ".property-title",
            ]

            for selector in title_selectors:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    text = element.text.strip()
                    if (
                        text
                        and len(text) > 5
                        and "404" not in text
                        and "403" not in text
                    ):
                        data["title"] = text
                        print(f"COLOMBIA Title: {text}")
                        break
                except:
                    continue
            else:
                data["title"] = "Not found"
                print("Title not found")

        except Exception as e:
            print(f"Error with title: {e}")
            data["title"] = "Error"

        try:
            # Price - specific for Colombia (COP)
            price_selectors = [
                "[data-qa='posting-price']",
                ".posting-price",
                ".price",
                "[class*='price']",
                ".price-value",
                "div[class*='price']",
                ".property-price",
            ]

            for selector in price_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        text = element.text.strip()
                        # Look for Colombian pesos
                        if text and (
                            "$" in text
                            or "COP" in text
                            or "cop" in text.lower()
                            or "pesos" in text.lower()
                        ):
                            data["price"] = text
                            print(f"COLOMBIA Price: {text}")
                            break
                    if "price" in data:
                        break
                except:
                    continue
            else:
                data["price"] = "Not found"
                print("Price not found")

        except Exception as e:
            print(f"Error with price: {e}")
            data["price"] = "Error"

        try:
            # Location - specific for Colombia
            location_selectors = [
                "[data-qa='posting-location']",
                ".posting-location",
                ".location",
                "[class*='location']",
                ".address",
                ".property-location",
            ]

            for selector in location_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        text = element.text.strip()
                        if text and len(text) > 3:
                            data["location"] = text
                            print(f"COLOMBIA Location: {text}")
                            break
                    if "location" in data:
                        break
                except:
                    continue
            else:
                data["location"] = "Not found"
                print("Location not found")

        except Exception as e:
            print(f"Error with location: {e}")
            data["location"] = "Error"

        # Additional info for Colombia
        try:
            # Area in m²
            area_selectors = [
                ".area",
                "[class*='area']",
                "[class*='size']",
                ".property-area",
            ]
            for selector in area_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        text = element.text.strip()
                        if text and (
                            "m²" in text or "mt2" in text or "metros" in text.lower()
                        ):
                            data["area"] = text
                            print(f"Area: {text}")
                            break
                    if "area" in data:
                        break
                except:
                    continue
        except:
            pass

        return data


def test_scraper_colombia():
    """Test that gets a real property from COLOMBIA and scrapes it"""

    print("Setting up driver...")
    print("🇨🇴 SPECIFIC TEST FOR COLOMBIA")

    # STEALTH setup - visible browser
    chrome_options = Options()

    # REMOVE headless - visible browser to avoid detection
    # chrome_options.add_argument("--headless=new")  # COMMENTED

    # Options to look more human
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)

    # Real user agent
    chrome_options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )

    driver = webdriver.Chrome(options=chrome_options)

    # Execute script to hide automation
    driver.execute_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    )

    try:
        print("Starting COLOMBIA test...")
        print("Searching real properties on Properati Colombia")

        # Step 1: Get a real property URL in COLOMBIA
        listing_scraper = SimpleListingScraper(driver)

        # Properati COLOMBIA search URLs
        search_urls = [
            "https://www.properati.com.co/s/venta",
            "https://www.properati.com.co/s/bogota/venta",
            "https://www.properati.com.co/s/medellin/venta",
            "https://www.properati.com.co/s/cali/venta",
        ]

        property_url = None
        for search_url in search_urls:
            print(f"\nTesting search at: {search_url}")
            property_url = listing_scraper.get_random_property_url(search_url)
            if property_url:
                break

        if not property_url:
            print("Could not get a property URL in Colombia")
            return False

        print(f"\nCOLOMBIA URL OBTAINED FROM SITE: {property_url}")

        # Step 2: Scrape the property
        detail_scraper = SimpleDetailScraper(driver)
        data = detail_scraper.scrape(property_url)

        print("\n" + "=" * 60)
        print("SCRAPING RESULTS - COLOMBIA")
        print("=" * 60)

        for key, value in data.items():
            print(f"   {key.capitalize()}: {value}")

        # Checks
        title_ok = data.get("title") not in ["Not found", "Error"] and data.get("title")
        price_ok = data.get("price") not in ["Not found", "Error"] and data.get("price")
        location_ok = data.get("location") not in ["Not found", "Error"] and data.get(
            "location"
        )

        if title_ok and price_ok:
            print("\nSUCCESSFUL TEST IN COLOMBIA!")
            print("   Title and price extracted correctly")
            if location_ok:
                print("   Location also extracted")
            return True
        else:
            print("\nTEST FAILED IN COLOMBIA")
            if not title_ok:
                print("   - Could not extract title")
            if not price_ok:
                print("   - Could not extract price")
            return False

    except Exception as e:
        print(f"Error during the test: {e}")
        import traceback

        traceback.print_exc()
        return False
    finally:
        print("\n🔚 Closing driver in 10 seconds...")
        time.sleep(10)
        driver.quit()


if __name__ == "__main__":
    print("🇨🇴 TEST: Scraping with real COLOMBIA URL")
    print("This test will open Chrome and search for properties in Colombia")

    confirmation = input("Run the test? (y/n): ")
    if confirmation.lower() == "y":
        success = test_scraper_colombia()
        if success:
            print("\nThe scraper works correctly in Colombia!")
        else:
            print("\nThe scraper has issues with properties in Colombia")
    else:
        print("Test cancelled")
