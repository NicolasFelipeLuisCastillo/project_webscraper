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
Scraper --> FileManager : uses

%% ==== NUEVAS RELACIONES ====
RealEstateScraper --> WebDriverController : controls
RealEstateScraper --> PropertyListScraper : uses
RealEstateScraper --> PropertyDetailScraper : uses
RealEstateScraper --> PropertyExporter : uses
PropertyDetailScraper --> WebDriverController : uses driver
PropertyListScraper --> WebDriverController : uses driver

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
