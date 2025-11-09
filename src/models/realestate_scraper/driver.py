import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

class WebDriverController:
    """Controlador de Selenium WebDriver."""

    def __init__(self, headless=False):
        self.driver = None
        self.headless = headless
        self.setup_driver()

    def setup_driver(self):
        options = Options()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        if self.headless:
            options.add_argument("--headless=new")
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        self.driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )

    def close(self):
        try:
            if self.driver:
                logging.info("Cerrando navegador...")
                self.driver.quit()
        except Exception as e:
            logging.warning(f"Error cerrando navegador: {e}")
