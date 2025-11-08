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
# Final Project OOP: Web Scraping System in Python

### National University of Colombia 
**Course:** Obejct Oriented Programming  
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

class WikiScraper {
    + parse(html)
}

class RealEstateScraper {
    + parse(html)
}

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

Scraper <|-- WikiScraper
Scraper <|-- RealEstateScraper

MainApp --> WikiScraper : uses
MainApp --> RealEstateScraper : uses
WikiScraper --> Parser : uses
RealEstateScraper --> Parser : uses
Scraper --> FileManager : uses

```
