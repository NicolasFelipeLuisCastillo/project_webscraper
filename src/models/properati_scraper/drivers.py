"""
WebDriver setup and management.
"""

import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium_stealth import stealth
from webdriver_manager.chrome import ChromeDriverManager

from .config import DEFAULT_HEADLESS


class WebDriverController:
    """Controller for managing WebDriver instances."""

    def __init__(self, headless=DEFAULT_HEADLESS):
        self.headless = headless
        self.driver = self._setup_driver()

    def _setup_driver(self):
        """Set up Chrome WebDriver with configured options."""
        options = Options()
        if self.headless:
            options.add_argument("--headless=new")

        options.add_argument("--start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-infobars")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)

        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=options
        )

        # Apply stealth settings to avoid detection
        stealth(
            driver,
            languages=["es-ES", "es"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
        )
        return driver

    def close(self):
        """Close the WebDriver instance."""
        try:
            if self.driver:
                self.driver.quit()
                logging.info("Browser closed.")
        except Exception as e:
            logging.warning(f"Error closing browser: {e}")
