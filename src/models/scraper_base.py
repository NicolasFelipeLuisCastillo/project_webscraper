import requests
import random
import time
from abc import ABC, abstractmethod
from utils.logger import get_logger

logger = get_logger(__name__)


class ScraperBase(ABC):
    def __init__(self, base_url: str, max_retries: int = 3):
        self.base_url = base_url
        self.max_retries = max_retries
        self.headers = {
            "User-Agent": "Mozilla/5.0 (compatible; WebScraperBot/1.0; +https://example.com/bot)"
        }

    def fetch(self, url: str) -> str:
        """Obtiene HTML con reintentos automáticos."""
        for attempt in range(self.max_retries):
            try:
                response = requests.get(url, headers=self.headers, timeout=10)
                response.raise_for_status()
                logger.info(f"Page succesfully downloaded: {url}")
                return response.text
            except requests.RequestException as e:
                logger.warning(
                    f"Error downloading {url}: {e}. Retrying ({attempt + 1}/{self.max_retries})"
                )
                time.sleep(random.uniform(1, 3))
        logger.error(
            f"Access to {url} was not possible after {self.max_retries} tries."
        )
        return ""

    @abstractmethod
    def parse(self, html: str):
        pass

    @abstractmethod
    def run(self):
        pass
