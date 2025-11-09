# Final Project OOP: Web Scraping System in Python

### National University of Colombia 
**Course:** Object Oriented Programming  
**Members:**  
- Nicolas Felipe Luis Castillo — Object-oriented design and version control 
- Juan Daniel Egoavil Cardozo — Real estate scraper
- Maycol David Lopez Largo — Data management and scraper base/wiki 

---

## Summary
This project implements a **web scraping** system in Python, designed using **Object-Oriented Programming (OOP) principles**.
The system aims to **extract information from Wiki-type sites** and **extract and organize real estate listings from a real estate portal** (e.g., Metrocuadrado, Ciencuadras, Properati, etc.), filtering the results by city or town.

All information is displayed on the console, but the architecture is prepared to be compatible with a future graphical user interface (GUI).

---

## Main Features

- Text extraction from Wiki-type sites (2 or 3 configurable URLs).
- Extraction and organization of real estate listings from a selected portal.
- Storage of cleaned and processed data in structured format (CSV).
- Modularity and extensibility through classes and inheritance.

## Class Diagram
``` mermaid
classDiagram
direction TB

%% ==== CLASE BASE ====
class Scraper {
    <<abstract>>
    - base_url: str
    - endpoints: list
    - session
    - data: list
    + __init__(base_url, endpoints)
    + fetch_html(endpoint)
    + parse(html)
    + save_data(filename, folder)
    + run()
}

%% ==== SUBCLASES ====
class WikiScraper {
    + parse(html)
}

class RealEstateScraper {
    - ctrl: WebDriverController
    - list_scraper: PropertyListScraper
    - detail_scraper: PropertyDetailScraper
    - save_every: int
    - sales_data: list
    - rentals_data: list
    - processed_urls: set
    + __init__(save_every)
    + parse(html)
    + fetch_html(endpoint)
    + run()
    + save_data(filename, folder)
}

%% ==== COMPONENTES AUXILIARES ====
class Parser {
    + extract_text(html)
    + extract_links(html)
}

class FileManager {
    + save_json(data, filename, folder)
    + load_json(filepath)
}

class MainApp {
    + run_wiki_scraper()
    + run_realestate_scraper()
    + show_results()
}

%% ==== CLASES NUEVAS ====
class WebDriverController {
    - driver
    + __init__()
    + setup_driver()
    + close()
}

class PropertyListScraper {
    - driver: webdriver.Chrome
    + __init__(driver)
    + extract_links_and_prices() List~Dict~
}

class PropertyDetailScraper {
    - driver: webdriver.Chrome
    - normalized_map: dict
    + __init__(driver)
    + extract_detail(url, title, price) Dict
    - _match_label(label_text)
    - _extract_from_dl(soup)
    - _extract_from_tables(soup)
    - _extract_from_lists(soup)
    - _extract_from_divs(soup)
}

class PropertyExporter {
    + ensure_folder_exists()
    + save_files(sales_data: List~Dict~, rentals_data: List~Dict~)
    + save_json(data: List~Dict~, filename: str)
}

%% ==== RELACIONES ====
Scraper <|-- WikiScraper
Scraper <|-- RealEstateScraper

MainApp --> WikiScraper : uses
MainApp --> RealEstateScraper : uses
WikiScraper --> Parser : uses
RealEstateScraper --> Parser : uses
Scraper --> FileManager : uses

%% ==== NUEVAS RELACIONES ====
RealEstateScraper --> WebDriverController : controls
RealEstateScraper --> PropertyListScraper : uses
RealEstateScraper --> PropertyDetailScraper : uses
RealEstateScraper --> PropertyExporter : uses
PropertyDetailScraper --> WebDriverController : uses driver
PropertyListScraper --> WebDriverController : uses driver


```
