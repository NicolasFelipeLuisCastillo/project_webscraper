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
# **Base Scraper Code Flow**  
## **Executive Summary**  
This is a modular and extensible HTTP-based web scraper designed to fetch and process HTML content from one or more endpoints. It uses the Requests library for network communication and stores the extracted data as JSON files. The scraper is implemented using an object-oriented base class (`Scraper`), which can be easily subclassed for specific use cases (e.g., parsing product pages, news articles, or APIs).  

## **Main Execution Flow**  
### **1. Initialization**  
scraper = Scraper(base_url="https://example.com", endpoints=["/page1", "/page2"])  
Initializes internal attributes: `base_url` (root domain for requests), `endpoints` (list of relative paths), `session` (persistent requests.Session), and `data` (empty list for parsed results).  

### **2. Fetching HTML Content**  
html = scraper.fetch_html(endpoint)  
For each endpoint, the scraper builds the full URL (`base_url + endpoint`), defines custom request headers (User-Agent, Accept-Language, etc.), sends a GET request using Requests, handles timeout or connection errors, and returns HTML text if successful or an empty string on failure. Key features include a custom User-Agent, configurable timeout (10s), and graceful error handling with try/except blocks.  

### **3. Parsing HTML Content**  
parsed_items = self.parse(html)  
The `parse()` method is abstract and must be implemented in a subclass. It defines how HTML content will be analyzed (e.g., with BeautifulSoup or regex) and returns a list or dictionary of extracted data. Example: def parse(self, html): soup = BeautifulSoup(html, "html.parser"); return [{"title": tag.text} for tag in soup.find_all("h2")]  

### **4. Data Aggregation**  
self.data.extend(parsed_items)  
Accumulates all parsed results into `self.data`, handles both single dictionaries and lists of dictionaries, ensuring all parsed information is collected for export.  

### **5. Data Export**  
scraper.save_data("output.json", folder="data")  
Saves data to JSON: checks if data exists, verifies/creates the folder, serializes to UTF-8 JSON, saves the file, and prints a confirmation message. If no data exists, prints "No data to save." Example path: `data/output.json`.  

### **6. Main Orchestration (run)**  
scraper.run()  
Execution steps: verifies endpoints, iterates over each endpoint (fetches HTML, parses it, appends to `self.data`), and prints the total number of items collected.  

## **Key Features of the Flow**  
- Modular Architecture: `Scraper` acts as a base class to be extended; promotes code reuse and separation of logic.  
- Robust Request Handling: can be extended with retries; uses persistent session for headers/cookies.  
- Flexible Output: JSON for easy integration; extendable to CSV, XML, or databases.  
- Separation of Concerns: `fetch_html()` handles requests, `parse()` handles extraction, `save_data()` handles persistence, `run()` orchestrates workflow.  

## **Data Flow**  
Base URL + Endpoints → Fetch HTML → Parse Data → Aggregate Results → Export JSON (data/output.json)  

## **Configuration and Limits**  
- Timeout: 10 seconds per request  
- Folder: "data" auto-created if missing  
- Output format: UTF-8 JSON  
- Custom headers: browser-like defaults  


# **RealEstateScraper Code Flow**  
## **Executive Summary**

This is an automated web scraper that extracts real estate property information using **Selenium** for dynamic navigation and **BeautifulSoup** for HTML parsing.

---

## **Main Execution Flow**

### **1. Initialization**
```python
scraper = RealEstateScraper()  # → _init_ is executed
```

- Configures the WebDriver with options to avoid detection  
- Initializes components: `list_scraper`, `detail_scraper`  
- Defines data structures: `sales_data`, `rentals_data`, `processed_urls`

---

### **2. Main Execution (run())**
```python
scraper.run()  # → Main orchestration method
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
