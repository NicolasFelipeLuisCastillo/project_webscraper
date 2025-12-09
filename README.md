<img width="781" height="319" alt="c2e1a376-86d6-4ad6-890b-b69256035a48-removebg-preview" src="https://github.com/user-attachments/assets/51cc1d8c-8662-43ac-ba74-73ff38443c5b" />
# Proyecto Final POO: Sistema de Web Scraping en Python

### Universidad Nacional de Colombia
**Curso:** Programación Orientada a Objetos
**Miembros:**
- Nicolás Felipe Luis Castillo — Diseño orientado a objetos y control de versiones
- Juan Daniel Egoavil Cardozo — Scraper inmobiliario
- Maycol David López Largo — Gestión de datos y base/wiki del scraper

---

## Resumen
Este proyecto implementa un sistema de **web scraping** en Python, diseñado con principios de **Programación Orientada a Objetos (POO)**.
El sistema busca **extraer información de Wikipedia** y **extraer y organizar listados de propiedades de Properati**

Toda la información se muestra en la consola, pero la arquitectura está preparada para ser compatible con una futura interfaz gráfica de usuario (GUI).

---

## Características principales

- Extracción de texto de Wikipedia.
- Extracción y organización de listados de inmuebles de un portal seleccionado.
- Almacenamiento de datos limpios y procesados ​​en formato estructurado (CSV).
- Modularidad y extensibilidad mediante clases y herencia.

---

## Flujo de trabajo
Para este proyecto se utilizó la metodología scrum realizando 2 sprints en el desarrollo de este mismo. Además, se utilizó clickup para controlar y programarlas tareas de cada uno de los integrantes.
<img width="1624" height="807" alt="Captura de pantalla 2025-12-06 170822" src="https://github.com/user-attachments/assets/95e1a001-cdca-42e8-8ea0-700091cb91c5" />


## Estructura del proyecto

``` css
src/
   ├── main.py
   │
   ├── models/
   │   ├── __init__.py
   │   │
   │   ├── wiki_scraper.py
   │   │
   │   └── properati_scraper/
   │       ├── __init__.py
   │       │
   │       ├── config.py
   │       ├── drivers.py
   │       ├── properati_main.py
   |       |
   │       ├── scrapers/
   │       │   ├── __init__.py
   │       │   ├── base_scraper.py
   │       │   ├── listing_scraper.py
   │       │   ├── detail_scraper.py
   │       │   └── project_scraper.py
   │       │
   │       ├── utils/
   │       │   ├── __init__.py
   │       │   ├── helpers.py
   │       │   └── file_handlers.py
   │       │
   │       └── properati_main.py
   │
   └── __init__.py
```



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
    + fetch_html(endpoint) str
    + parse(html)
    + save_data(filename, folder)
    + run()
}

%% ==== COMPONENTES PRINCIPALES ====
class SeleniumBaseScraper {
    - driver
    + __init__(driver)
    + wait_for_page_load(timeout) bool
    + scrape_with_captcha_protection(url, timeout) str
    + scroll_page(scroll_pause, max_scrolls)
}

class ProperatiScraper {
    - mode: str
    - max_pages: int
    - requests_per_minute: int
    - scrape_project_units: bool
    - ctrl: WebDriverController
    - data_handler: DataHandler
    - listing_scraper: ListingScraper
    - detail_scraper: DetailScraper
    - project_scraper: ProjectScraper
    - properties_processed: int
    - backup_counter: int
    + __init__(mode, max_pages, headless, requests_per_minute, scrape_project_units)
    + parse(html)
    + _handle_captcha()
    + _save_data_incremental(new_properties_count, force_save)
    + run()
}

class WebDriverController {
    - headless: bool
    - driver
    + __init__(headless)
    + _setup_driver()
    + close()
}

class ListingScraper {
    + __init__(driver)
    + extract_links_from_soup(soup) list
    + extract_links(url) list
    + check_pagination_limit(soup, page_num) bool
}

class DetailScraper {
    + __init__(driver)
    + _extract_garage_specific(soup) str
    + _extract_description(soup) str
    + _extract_features(soup) list
    + _extract_half_bathrooms(soup) str
    + _extract_floor_level(soup) str
    + _parse_detalle_html(html, url) dict
    + _parse_proyecto_html(html, url) dict
    + scrape_property(url) dict
}

class ProjectScraper {
    + __init__(driver)
    + extract_unit_links(project_url) list
    + _extract_project_details(soup) dict
    + _extract_project_info(soup, project_url) dict
    + scrape_unit_property(unit_url) dict
    + scrape_project_with_units(project_url) list
}

class DataHandler {
    - csv_filename: str
    - json_filename: str
    + __init__()
    + _initialize_filenames()
    + save_data(data, force_save)
    + generate_statistics(data) dict
    + log_statistics(data)
}

class Helpers {
    <<static>>
    + ensure_folder_exists(folder_path)
    + human_pause(base, jitter)
    + safe_extract(soup, selectors, default) str
    + extract_numeric_value(soup, data_test_attribute, context_keywords, default) str
    + extract_business_type(url, soup) str
    + detect_captcha(html) bool
}

class Config {
    <<static>>
    - BASE_URL: str
    - DATA_FOLDER: str
    - BACKUP_INTERVAL: int
    - DEFAULT_MAX_PAGES: int
    - DEFAULT_REQUESTS_PER_MINUTE: int
    - DEFAULT_HEADLESS: bool
    - LINK_SELECTORS: list
    - TITLE_SELECTORS: list
    - PRICE_SELECTORS: list
    - LOCATION_SELECTORS: list
    - BEDROOM_KEYWORDS: list
    - BATHROOM_KEYWORDS: list
    - GARAGE_KEYWORDS: list
    - LOT_KEYWORDS: list
    - CAPTCHA_INDICATORS: list
}

class PropertyData {
    + URL: str
    + Title: str
    + Neighborhood: str
    + Price: str
    + Built_Area: str
    + Land_Area: str
    + Bedrooms: str
    + Bathrooms: str
    + Half_Bathrooms: str
    + Garage: str
    + Stratum: str
    + Year_Built: str
    + Floor_Level: str
    + Administration_Fee: str
    + Property_Type: str
    + Business_Type: str
    + Status: str
    + Extraction_Date: str
    + Error: str
    + Property_Category: str
    + Description: str
    + Features: str
    + Features_Count: str
    + Is_Project: str
    + Project_Parent: str
    + Project_Name: str
    + Is_Project_Unit: str
}

%% ==== RELACIONES ====
Scraper <|-- ProperatiScraper
SeleniumBaseScraper <|-- ListingScraper
SeleniumBaseScraper <|-- DetailScraper
SeleniumBaseScraper <|-- ProjectScraper

ProperatiScraper --> WebDriverController
ProperatiScraper --> DataHandler
ProperatiScraper --> ListingScraper
ProperatiScraper --> DetailScraper
ProperatiScraper --> ProjectScraper

ListingScraper --> Helpers
DetailScraper --> Helpers
ProjectScraper --> Helpers
ProperatiScraper --> Helpers

Config --> Helpers
Config --> ListingScraper
Config --> DetailScraper
Config --> ProjectScraper
Config --> ProperatiScraper

DetailScraper --> PropertyData
ProjectScraper --> PropertyData

```

