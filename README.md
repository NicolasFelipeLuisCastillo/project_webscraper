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

---

## Cómo instalar y ejecutar?
### Clonar el repositorio desde github
``` git
git clone 
```
### Entrar al proyecto
``` git
cd project_webscraper
```
### Crear un entorno virtual
En terminal
``` bash
python -m venv venv 
```
Activarlo
``` bash
venv\Scripts\activate 
```
### Instalar dependendencias
``` bash
pip install -r requiriments.txt 
```
### Ejecutar en la terminal:
``` bash
python -m src.main
```

---

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

## Diagrama de clases
``` mermaid
classDiagram
    %% Base Classes
    class Scraper {
        +str base_url
        +list endpoints
        +Session session
        +list data
        +__init__(base_url, endpoints)
        +fetch_html(endpoint) str
        +parse(html) abstract
        +save_data(filename, folder)
        +run()
    }

    class SeleniumBaseScraper {
        +WebDriver driver
        +__init__(driver)
        +wait_for_page_load(timeout) bool
        +scrape_with_captcha_protection(url, timeout) str
        +scroll_page(scroll_pause, max_scrolls)
    }

    %% Wiki Scraper
    class WikiScraper {
        +__init__(base_url, endpoints)
        +parse(html) dict
    }

    %% Properati Components
    class WebDriverController {
        +bool headless
        +WebDriver driver
        +__init__(headless)
        -_setup_driver() WebDriver
        +close()
    }

    class ProperatiScraper {
        +str mode
        +int max_pages
        +int requests_per_minute
        +bool scrape_project_units
        +WebDriverController ctrl
        +DataHandler data_handler
        +ListingScraper listing_scraper
        +DetailScraper detail_scraper
        +ProjectScraper project_scraper
        +list data
        +int properties_processed
        +int backup_counter
        +__init__(mode, max_pages, headless, requests_per_minute, scrape_project_units)
        +parse(html) list
        -_handle_captcha()
        -_save_data_incremental(new_properties_count, force_save)
        +run()
    }

    class ListingScraper {
        +__init__(driver)
        +extract_links_from_soup(soup) list
        +extract_links(url) list
        +check_pagination_limit(soup, page_num) bool
    }

    class DetailScraper {
        +__init__(driver)
        -_extract_garage_specific(soup) str
        -_extract_description(soup) str
        -_extract_features(soup) list
        -_extract_half_bathrooms(soup) str
        -_extract_floor_level(soup) str
        -_parse_detalle_html(html, url) dict
        -_parse_proyecto_html(html, url) dict
        +scrape_property(url) dict
    }

    class ProjectScraper {
        +__init__(driver)
        +extract_unit_links(project_url) list
        -_extract_project_details(soup) dict
        -_extract_project_info(soup, project_url) dict
        +scrape_unit_property(unit_url) dict
        +scrape_project_with_units(project_url) list
    }

    class DataHandler {
        +str csv_filename
        +str json_filename
        +__init__()
        -_initialize_filenames()
        +save_data(data, force_save)
        +generate_statistics(data) dict
        +log_statistics(data)
    }

    %% Relationships
    Scraper <|-- WikiScraper : inherits
    Scraper <|-- ProperatiScraper : inherits
    SeleniumBaseScraper <|-- ListingScraper : inherits
    SeleniumBaseScraper <|-- DetailScraper : inherits
    SeleniumBaseScraper <|-- ProjectScraper : inherits
    
    ProperatiScraper *-- WebDriverController : composition
    ProperatiScraper *-- DataHandler : composition
    ProperatiScraper *-- ListingScraper : composition
    ProperatiScraper *-- DetailScraper : composition
    ProperatiScraper *-- ProjectScraper : composition
    
    ListingScraper ..> WebDriverController : uses
    DetailScraper ..> WebDriverController : uses
    ProjectScraper ..> WebDriverController : uses
    
    %% Helper Classes
    class Helpers {
        <<utility>>
        +ensure_folder_exists(folder_path)
        +human_pause(base, jitter)
        +safe_extract(soup, selectors, default) str
        +extract_numeric_value(soup, data_test_attribute, context_keywords, default) str
        +extract_business_type(url, soup) str
        +detect_captcha(html) bool
    }
    
    ProperatiScraper ..> Helpers : uses
    DetailScraper ..> Helpers : uses
    ProjectScraper ..> Helpers : uses
```
---

## Solución tarea 1: WikiScraper
### Clase WikiScraper
Enfoque: Scraping basado en requests (HTTP simple)
Características:
- Usa herencia de `Scraper` base
- Implementa `parse()` específico para estructura HTML de Wikipedia.
Output: Archivos csv y json con el título y el contenido de la página.

### Flujo wiki_scraper.py
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

---

## Solución Tarea 2: Properati
Clase principal: `ProperatiScraper`
Enfoque: Scraping basado en Selenium (navegador automatizado)

¿Por qué Selenium y no requests?
| Aspecto | Requests | Selenium |
|---------|----------|----------|
| Javascript| No ejecuta | Si ejecuta |
| Contenido dinámico | No carga | Carga todo |
| Detección antibot | Díficil de detectar | Fácil de detectar (necesita stealth)|
| Velocidad | Rápido | Lento |

---

### Componentes Especializados
### 1. WebDriverController ubicado en drivers.py
Uso de `selenium-stealth` para evitar detección de automatización.

- Inicializar Chrome
Con headless o no.

- Configurar:
   - user-agent
   - anti-detección
   - opciones stealth

- Reiniciar el driver
Si ocurre un CAPTCHA.

- Cerrar el navegador
  
### Flujo drivers.py
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
---
### 2. ListingScraper
Diseño: Usa múltiples selectors porque la estructura HTML puede variar.

Responsable de:

- abrir páginas de listado
- hacer scroll infinito
- detectar el límite de paginación
- extraer enlaces a:
   - /detalle/
   - /proyecto/

- limpiar enlaces
- manejar HTML con BeautifulSoup

### Flujo listing_scraper.py

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
--- 
### 3. DetailScraper
Características técnicas:
- Extracción resiliente: Múltiples selectores fallback
- Lógica condicional: Diferencia lotes de construcciones
- Métodos especializados: _extract_garage_specific() maneja casos complejos
### Flujo detail_scraper.py

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
---
### 4. ProjectScraper
Muchos listados son proyectos.
Este scraper:
- 1. Scrapea la página general del proyecto
- 2. Extrae info (amenities, áreas, constructor)
- 3. Encuentra todas las unidades
- 4. Scrapea cada unidad individual
- 5. Envía todo el conjunto al DataHandler
Produce varios objetos “propiedad” por un solo proyecto.

### Flujo project_scraper.py

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
---
### Funciones utilitarias (helpers.py)



### Archivo config.py
Contiene:
- URL base: https://www.properati.com.co
- Selectores CSS para:
   - precio
   - título
   - barrio
   - área
   - habitaciones
   - baños
   - garajes
- Configuración Selenium
- Límite de páginas
- Palabras clave
- Carpetas de datos

---
### Archivo properati_main.py

Orquesta el scraper completo de Properati.

Contiene:
- Clase ProperatiScraper (motor principal)
Funciones:

**1. Inicialización**

Crea:
   - WebDriverController
   - ListingScraper
   - DetailScraper
   - ProjectScraper
   - DataHandler

Define parámetros:
   - modo (venta / arriendo / todos)
   - páginas máximas
   - requests por minuto
   - headless
   - scraping de unidades en proyectos

**2. _handle_captcha()**

Cuando detecta CAPTCHA:
   - espera 3–5 minutos
   - reinicia Selenium
   - reinstancia los scrapers
   - continúa donde quedó
Robustez real de un scraper profesional.

**3. _save_data_incremental()**

Guarda cada:
   - X propiedades
   - cada proyecto
   - cada página
   - cada error

Evita pérdida total si Selenium falla.

**4. run() — flujo principal**

- 1. recorre páginas de venta / arriendo
- 2. extrae enlaces
- 3. maneja CAPTCHA
- 4. procesa:

   - proyectos completos

   - propiedades individuales

- 5. pausa entre requests para evitar bloqueo

- 6. guarda incremental

- 7. guarda todo al final

- 8. cierra Selenium

Este método integra todas las piezas del sistema.

**5. main()**

Permite ejecutar el scraper directamente como:

python properati_main.py

Configura:
- logging
- páginas
- modo de scraping
- frecuencia de requests
  
### Flujo properati_main.py
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



## Flujo properati_main.py


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


