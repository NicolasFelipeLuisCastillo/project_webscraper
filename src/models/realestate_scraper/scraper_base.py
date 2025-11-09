import requests
import json
import os


class Scraper:
    def __init__(self, base_url=None, endpoints=None):
        self.base_url = base_url or ""
        self.endpoints = endpoints or []
        self.session = requests.Session()
        self.data = []

    def fetch_html(self, endpoint):
        url = self.base_url + endpoint
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()  # Raises HTTPError if response is not 200 OK
            return response.text
        except requests.exceptions.RequestException as error:
            print("Request failed:", error)
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
