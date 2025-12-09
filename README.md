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
## Flujo wiki_scraper.py

``` mermaid
flowchart TD

    A[WikiScraper inicia] --> B[Recibir base_url y endpoints]
    B --> C[Iterar endpoints]

    C --> D[fetch_html con requests]
    D --> E{Hubo error?}
    E -->|Si| F[Retornar dict con error]
    E -->|No| G[Pasar HTML a parse]

    G --> H[Crear BeautifulSoup]
    H --> I[Obtener titulo de h1]
    I --> J[Obtener contenedor principal]

    J --> K[Extraer parrafos]
    K --> L[Combinar texto]

    L --> M[Construir dict con title y content]
    M --> N[Agregar resultado a lista data]

    N --> O{Quedan endpoints?}
    O -->|Si| C
    O -->|No| P[Retornar data final]

```

## Flujo drivers.py

``` mermaid
flowchart TD

    A[Crear instancia WebDriverController] --> B[Init controlador]
    B --> C[Llamar a create driver]

    C --> D[Configurar ChromeOptions]
    D --> E[Agregar flags y opciones]

    E --> F[Aplicar anti deteccion]
    F --> G[Inicializar Chrome con driver]

    G --> H[Agregar script para ocultar webdriver]
    H --> I[Driver Selenium listo]

    I --> J[ListingScraper usa driver]
    I --> K[DetailScraper usa driver]
    I --> L[ProjectScraper usa driver]

    J --> M[Acceso Selenium]
    K --> M
    L --> M

    M --> N{Captcha?}

    N -->|Si| O[Cerrar driver]
    O --> P[Recrear WebDriverController]
    P --> C

    N -->|No| Q[Continuar scraping]

    Q --> R[Cierre final del driver]
```
## Flujo listing_scraper.py

``` mermaid
flowchart TD

    A[ListingScraper inicia] --> B[Recibir driver]
    B --> C[Cargar pagina de listado]
    C --> D[Scroll en pagina]
    D --> E[Obtener HTML page_source]

    E --> F[Parsear con BeautifulSoup]
    F --> G[Extraer links de propiedades y proyectos]

    G --> H{Hay paginacion extra?}
    H -->|Si| I[Continuar paginas]
    H -->|No| J[Detener]

    I --> C
    J --> K[Retornar lista de links]

```
## Flujo detail_scraper.py

``` mermaid
flowchart TD

    A[DetailScraper inicia] --> B[Recibir driver]
    B --> C[Acceder a URL propiedad]

    C --> D[Detectar captcha]
    D -->|Captcha| E[Retornar None]

    D -->|OK| F[Obtener HTML]
    F --> G[Parsear con BeautifulSoup]

    G --> H[Extraer datos: precio, area, cuartos]
    H --> I[Extraer datos: banos, garajes]
    I --> J[Extraer descripcion y amenities]

    J --> K{Es proyecto?}
    K -->|Si| L[Retornar indicador de proyecto]
    K -->|No| M[Retornar dict propiedad]

```
## Flujo project_scraper.py

``` mermaid
flowchart TD

    A[ProjectScraper inicia] --> B[Acceder a URL de proyecto]

    B --> C[Detectar captcha]
    C -->|Captcha| D[Retornar None]

    C -->|OK| E[Obtener HTML principal]

    E --> F[Extraer datos generales del proyecto]
    F --> G[Extraer lista de unidades]

    G --> H[Iterar unidades]
    H --> I[Scrapear unidad]
    I --> J[Agregar unidad al dataset]

    J --> K{Quedan unidades?}
    K -->|Si| H
    K -->|No| L[Retornar lista de unidades]

    L --> M[Incluir datos del proyecto en las unidades]

```
## Flujo properati_main.py

``` mermaid
flowchart TD

    A[ProperatiScraper inicia] --> B[Crear WebDriverController]
    B --> C[Crear ListingScraper DetailScraper ProjectScraper]
    C --> D[Definir modo venta arriendo]

    D --> E[Recorrer secciones]
    E --> F[Recorrer paginas]

    F --> G[Construir URL]
    G --> H[Scrape con proteccion captcha]

    H --> I{Captcha?}
    I -->|Si| J[Manejar captcha]
    J --> K[Reiniciar driver]
    K --> F

    I -->|No| L[Parsear con BeautifulSoup]
    L --> M[Extraer links]

    M --> N{Hay links?}
    N -->|No| O[Pasar a siguiente pagina]
    N -->|Si| P[Procesar cada link]

    P --> Q{Es proyecto?}
    Q -->|Si| R[Scrapear proyecto con unidades]
    Q -->|No| S[Scrapear propiedad individual]

    R --> T[Guardar data incremental]
    S --> T

    T --> U[Acumular propiedades]
    U --> F

    F --> V[Fin de paginas]
    V --> W[Guardar data final]
    W --> X[Guardar estadisticas]
    X --> Y[Cerrar driver]

```
## Flujo helpers.py

``` mermaid
flowchart TD

    A[helpers.py] --> B[safe_extract]
    B --> C[Intentar selector primario]
    C --> D{Existe valor?}
    D -->|Si| E[Retornar texto]
    D -->|No| F[Intentar selectores alternos]
    F --> E

    A --> G[extract_numeric_value]
    G --> H[Limpiar texto]
    H --> I[Buscar numeros]
    I --> J[Retornar numero o None]

    A --> K[extract_business_type]
    K --> L[Buscar palabras clave venta arriendo]
    L --> M[Retornar tipo]

    A --> N[detect_captcha]
    N --> O[Buscar patrones captcha]
    O --> P[Retornar True o False]

    A --> Q[human_pause]
    Q --> R[Calcular pausa aleatoria]
    R --> S[time.sleep]

```
## Flujo file_handlers.py

``` mermaid
flowchart TD

    A[file_handlers.py] --> B[save_data]
    B --> C[Generar nombre archivo]
    C --> D[Guardar JSON]
    C --> E[Guardar CSV]

    A --> F[log_statistics]
    F --> G[Contar propiedades]
    G --> H[Contar proyectos]
    H --> I[Guardar reporte txt]

    A --> J[ensure_folder]
    J --> K[Crear carpeta si no existe]

    A --> L[create_unique_filename]
    L --> M[Agregar timestamp]
    M --> N[Retornar nombre unico]

```
## Diagrama de clase de properati simple

``` mermaid
classDiagram

    class WebDriverController {
        +driver
        +headless
        +create_driver()
        +close()
        +restart()
    }

    class ListingScraper {
        +driver
        +extract_links()
        +check_pagination_limit()
    }

    class DetailScraper {
        +driver
        +scrape_property()
        +scrape_with_captcha()
    }

    class ProjectScraper {
        +driver
        +scrape_project_with_units()
    }

    class DataHandler {
        +save_data()
        +log_statistics()
        +unique_filename()
    }

    class ProperatiScraper {
        +run()
        +handle_captcha()
        +save_incremental()
    }

    ProperatiScraper --> WebDriverController
    ProperatiScraper --> ListingScraper
    ProperatiScraper --> DetailScraper
    ProperatiScraper --> ProjectScraper
    ProperatiScraper --> DataHandler

```
## Diagrama de secuencia

``` mermaid
sequenceDiagram
    participant P as ProperatiScraper
    participant D as WebDriverController
    participant L as ListingScraper
    participant T as DetailScraper
    participant J as ProjectScraper
    participant H as DataHandler

    P ->> D: Crear driver
    P ->> L: Extraer links de pagina
    L ->> D: driver.get(url)
    L ->> P: Retornar lista de links

    loop por cada link
        P ->> T: Scrapear propiedad
        T ->> D: driver.get(link)
        T ->> P: Retornar dict propiedad

        P ->> H: Guardar incremental
        H ->> P: Confirmar guardado
    end

    P ->> H: Guardado final
    H ->> P: Confirmar
    P ->> D: Cerrar driver

```


