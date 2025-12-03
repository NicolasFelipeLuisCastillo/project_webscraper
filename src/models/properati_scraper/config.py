"""
Configuration settings for Properati scraper.
"""

# Base configuration
BASE_URL = "https://www.properati.com.co"
DATA_FOLDER = "realestate_data"
BACKUP_INTERVAL = 12  # Save every 12 properties

# Scraping settings
DEFAULT_MAX_PAGES = 3
DEFAULT_REQUESTS_PER_MINUTE = 15
DEFAULT_HEADLESS = True

# Time settings
HUMAN_PAUSE_BASE = 1.5
HUMAN_PAUSE_JITTER = 0.8
SCROLL_PAUSE = 1.2
MAX_SCROLLS = 6

# Selectors for data extraction
LINK_SELECTORS = [
    "a[href*='/detalle/']",
    "a[href*='/proyecto/']",
    "article.snippet a",
    ".listing-card a",
    "[data-url]",
]

TITLE_SELECTORS = [".main-title h1", "h1.title", "[data-test='listing-title']", "h1"]

PRICE_SELECTORS = [
    "[data-test='listing-price']",
    ".prices-and-fees__price",
    ".price",
    ".listing-price",
    ".value",
]

LOCATION_SELECTORS = [
    ".location",
    "[data-test='location']",
    ".property-location",
    ".address",
]

# Keywords for data extraction
BEDROOM_KEYWORDS = [
    "habitacion",
    "habitaciones",
    "dormitorio",
    "dormitorios",
    "room",
    "bedroom",
]
BATHROOM_KEYWORDS = ["baño", "baños", "bath", "bathroom"]
GARAGE_KEYWORDS = ["garaje", "estacionamiento", "parqueadero", "parking", "garage"]
LOT_KEYWORDS = ["lote", "terreno", "finca", "parcela", "solar"]

# CAPTCHA detection
CAPTCHA_INDICATORS = [
    "Security verification",
    "math problem",
    "To continue, please complete",
    "captcha",
    "challenge",
]
