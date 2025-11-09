# realestate_scraper/run_scraper.py

import logging
import sys
import os

# Asegurarnos de que la carpeta padre esté en sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scraper import RealEstateScraper

logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    logging.info("Iniciando RealEstateScraper...")
    scraper = RealEstateScraper(
        base_url="https://bogotarealestate.com.co",
        max_pages=1,       # Cambia a la cantidad de páginas que quieras scrapear
        save_every=12      # Guarda cada 5 propiedades
    )
    scraper.run()
