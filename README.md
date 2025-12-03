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
    + fetch_html(endpoint) str
    + parse(html)
    + save_data(filename, folder)
    + run()
}

<<<<<<< HEAD
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
=======
%% ==== SUBCLASES ====
class WikiScraper {
>>>>>>> b14309afb9a099535bbd500459d600aa8868b485
    + parse(html)
    + _handle_captcha()
    + _save_data_incremental(new_properties_count, force_save)
    + run()
}

<<<<<<< HEAD
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
=======
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
>>>>>>> b14309afb9a099535bbd500459d600aa8868b485
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

<<<<<<< HEAD
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

Scraper <|-- ProperatiScraper
SeleniumBaseScraper <|-- ListingScraper
SeleniumBaseScraper <|-- DetailScraper
SeleniumBaseScraper <|-- ProjectScraper

ProperatiScraper --> WebDriverController : composes
ProperatiScraper --> DataHandler : composes
ProperatiScraper --> ListingScraper : composes
ProperatiScraper --> DetailScraper : composes
ProperatiScraper --> ProjectScraper : composes

ListingScraper --> Helpers : uses
DetailScraper --> Helpers : uses
ProjectScraper --> Helpers : uses
ProperatiScraper --> Helpers : uses

Config --> Helpers : provides
Config --> ListingScraper : provides
Config --> DetailScraper : provides
Config --> ProjectScraper : provides
Config --> ProperatiScraper : provides

DataHandler --> ProperatiScraper : used_by
WebDriverController --> ListingScraper : provides_driver
WebDriverController --> DetailScraper : provides_driver
WebDriverController --> ProjectScraper : provides_driver

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

DetailScraper --> PropertyData : creates
ProjectScraper --> PropertyData : creates
```
# **Base Scraper Code Flow**  
## **Executive Summary**  
This is a modular and extensible HTTP-based web scraper designed to fetch and process HTML content from one or more endpoints. It uses the Requests library for network communication and stores the extracted data as JSON files. The scraper is implemented using an object-oriented base class (`Scraper`), which can be easily subclassed for specific use cases (e.g., parsing product pages, news articles, or APIs).  
=======
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
Scraper --> FileManager : uses

%% ==== NUEVAS RELACIONES ====
RealEstateScraper --> WebDriverController : controls
RealEstateScraper --> PropertyListScraper : uses
RealEstateScraper --> PropertyDetailScraper : uses
RealEstateScraper --> PropertyExporter : uses
PropertyDetailScraper --> WebDriverController : uses driver
PropertyListScraper --> WebDriverController : uses driver
>>>>>>> b14309afb9a099535bbd500459d600aa8868b485

```

#### **2.1 Section Configuration**
```python
sections = {
    "Sales": "sales_search_URL",
    "Rentals": "rentals_search_URL"
}
```

#### **2.2 Loop Through Sections and Pages**
```text
For each section (Sales/Rentals):
    │
    ├── For each page (up to MAX_PAGES):
    │   │
    │   ├── Build page URL
    │   ├── Navigate with Selenium
    │   ├── Wait for load using WebDriverWait
    │   ├── Simulated human pause
    │   │
    │   └── Extract properties from list:
    │       │
    │       └── For each property in the list:
    │           │
    │           ├── Check for duplicates
    │           ├── Navigate to detail page
    │           ├── Extract detailed information
    │           ├── Normalize and map fields
    │           └── Store in the corresponding list
    │
    └── End section
```
|

---

### **3. Listing Processing (PropertyListScraper)**
```python
extract_links_and_prices()  # → Extracts from listing pages
```

- Finds property cards using multiple CSS selectors  
- Extracts: URL, title, price  
- Normalizes relative URLs to absolute  
- Uses fallbacks when expected elements are not found

---

### **4. Detail Processing (PropertyDetailScraper)**
```python
extract_detail(url, title, price)  # → Extracts complete information
```

- Navigates to the property’s individual page  
- Attempts multiple extraction strategies:
  - Definition lists (`<dl><dt><dd>`)
  - Tables (`<table><tr><td>`)
  - Unordered lists (`<ul><li>`)
  - Divs with specific patterns  
- Maps Spanish → English fields using `FIELD_MAP`  
- Handles errors with retries (`MAX_RETRIES`)

---

### **5. Data Export (PropertyExporter)**
```python
save_files(sales_data, rentals_data)  # → Saves results
```

- Creates CSV files: sales, rentals, combined  
- Generates a JSON file with all data  
- Folder structure: `realestate_data/`

---

## **Key Features of the Flow**

### **Navigation Handling**
- Human-like pauses with random delays  
- Explicit waits for critical elements  
- Automatic retries on failures  
- Duplicate control using `processed_urls`

---

### **Multiple Extraction Strategies**
```python
# Four different methods to find data
extraction_methods = [
    self._extract_from_dl,      # Definition lists
    self._extract_from_tables,  # HTML tables
    self._extract_from_lists,   # Unordered lists
    self._extract_from_divs     # Divs with specific patterns
]
```

---

### **Intelligent Field Mapping**
```python
FIELD_MAP = {
    "país": "Country",
    "departamento": "State", 
    "ciudad": "City",
    "área construida": "Built Area",
    # ... more mappings
}
```

---

### **Robust Error Handling**
- Retries on loading failures  
- Partial data saving on critical errors  
- Detailed logging for debugging  
- Continues after individual errors

---

## **Data Flow**
```text
Base URLs → Property Lists → Detail Pages → 
Normalized Data → CSV/JSON Files
```

---

## **Configuration and Limits**
- `MAX_PAGES = 1` (for testing only)  
- `SAVE_BATCH = 5` (how often to save)  
- `MAX_RETRIES = 3` (retries per property)  
- Human-like pauses between **3.5–4.5 seconds**
