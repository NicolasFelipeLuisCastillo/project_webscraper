import requests
import json
import os


class Scraper:
    def __init__(self, base_url=None, endpoints=None):
        self.base_url = base_url or ""
        self.endpoints = endpoints or []
        self.session = requests.Session()
        self.data = []

    def fetch_html(self, endpoint: str) -> str:
        url = f"{self.base_url}{endpoint}"
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Connection": "keep-alive",
        }

        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return ""

    def parse(self, html):
        raise NotImplementedError("Subclasses must implement the parse() method.")

    def save_data(self, filename, folder="data"):
        if not self.data:
            print("No data to save.")
            return

        if not os.path.exists(folder):
            os.makedirs(folder)

        path = os.path.join(folder, filename)

        try:
            with open(path, "w", encoding="utf-8") as file:
                json.dump(self.data, file, indent=4, ensure_ascii=False)
            print(f"Data successfully saved to {path}")
        except IOError as error:
            print("Error saving data:", error)

    def run(self):
        if not self.endpoints:
            print("No endpoints defined.")
            return

        for endpoint in self.endpoints:
            html = self.fetch_html(endpoint)
            if not html:
                continue

            parsed_items = self.parse(html)
            if parsed_items:
                if isinstance(parsed_items, list):
                    self.data.extend(parsed_items)
                else:
                    self.data.append(parsed_items)

        print("Scraping completed. Total items:", len(self.data))
