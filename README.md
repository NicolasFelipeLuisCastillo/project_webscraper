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
Para este proyecto se utilizó la metodología scrum realizando 2 sprints en el desarrollo de este mismo. Además, se utilizó clickup para controlar y programar las tareas de cada uno de los integrantes.
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
Método self_extract -> Prueba múltiples selectores hasta encontrar uno válido
¿Por qué múltiples selectores?
- Properati puede cambiar su HTML.
- Diferentes tipos de propiedades tienen estructuras diferentes
- Esto hace el scraper mas robusto

Método extract_numeric_value -> Extracción inteligente
Estrategia Fallback: si falla un método, prueba otro

### Flujo helpers.py

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
---

## Desafíos Técnicos

### 1. Detección y Manejo de CAPTCHA
Problema: Properati bloquea bots con CAPTCHA
Solución: 
- 1. Detectar CAPTCHA temprano
- 2. Esperar tiempo aleatorio (parecer humano)
- 3. Reiniciar navegador (nueva sesión)
- 4. Continuar desde donde se quedó
 
### 2. Guardado Incremental
Problema: Si el scraper se interrumpe (error, CAPTCHA) se pierde todo.
Solución:
Se guarda cada 12 intervalos usando el método protegido `save_data_incremental`. Con este método se pierden 11 propiedades en caso de fallo

### 3. Simulación de Comportamiento Humano
Problema: Comportamiento robótico es detectado.
Soluciones:
- 1. Se añadió una pausa humana aleatoria.
- 2. Se planteó un límite de solicitudes por minuto
- 3. Se añadió un scroll a la página para cargar el contenido dinámico

### 4. Extracción específica: Garajes.
Problema: Confusión entre "120 metros cuadrados" y 2 garajes.
Solución:
Se plantearon keywords para buscar garajes en lugar de áreas.

## Gestión y persistencia de datos
### Clase especializada DataHandler
Características:
- Dual format: CSV (análisis) + JSON (programático)
- Timestamps: Cada ejecución genera archivos únicos
- Estadísticas automáticas: Resumen post-scraping
