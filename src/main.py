import os
import sys

# Asegurar que src/ esté en sys.path
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# Imports (paquetes)
from src.models.wiki_scraper import WikiScraper
from src.models.properati_scraper.properati_main import ProperatiScraper


def mostrar_menu():
    print("\n==============================")
    print("       SELECCIONA SCRAPER")
    print("==============================")
    print("1) Properati Scraper")
    print("2) Wiki Scraper")
    print("0) Salir\n")
    return input("Seleccione una opción: ").strip()


def main():
    opcion = mostrar_menu()

    if opcion == "1":
        print("\n➡ Ejecutando ProperatiScraper...\n")
        scraper = ProperatiScraper(
            mode="venta",
            max_pages=1,
            headless=True,
            requests_per_minute=30,
            scrape_project_units=True,
        )
        scraper.run()
        print("\n✔ ProperatiScraper finalizado.\n")

    elif opcion == "2":
        print("\n➡ Ejecutando WikiScraper...\n")
        scraper = WikiScraper()
        result = scraper.run()
        print("\n✔ WikiScraper finalizado.")
        print(result)

    elif opcion == "0":
        print("Saliendo...")
        return
    else:
        print("Opción inválida.")


if __name__ == "__main__":
    main()
