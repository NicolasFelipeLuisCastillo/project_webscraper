"""
Utility functions and helpers.
"""

import time
import random
import os
import re
import logging

from bs4 import BeautifulSoup
from src.models.properati_scraper.config import HUMAN_PAUSE_BASE, HUMAN_PAUSE_JITTER


def ensure_folder_exists(folder_path):
    """Create folder if it doesn't exist."""
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        logging.info(f"Folder created: {folder_path}")


def human_pause(base=HUMAN_PAUSE_BASE, jitter=HUMAN_PAUSE_JITTER):
    """Human-like pause with random variation."""
    time.sleep(base + random.random() * jitter)


def safe_extract(soup, selectors, default="N/A"):
    """
    Safely extract text using multiple selectors.

    Args:
        soup: BeautifulSoup object
        selectors: List of CSS selectors to try
        default: Default value if no match found

    Returns:
        Extracted text or default value
    """
    for selector in selectors:
        element = soup.select_one(selector)
        if element:
            text = element.get_text(strip=True)
            if text and text not in ["", "-"]:
                return text
    return default


def extract_numeric_value(soup, data_test_attribute, context_keywords, default="N/A"):
    """
    Extract numeric value from elements with specific context.

    Args:
        soup: BeautifulSoup object
        data_test_attribute: data-test attribute value to search for
        context_keywords: Keywords to identify the context
        default: Default value if no match found

    Returns:
        Extracted numeric value or default
    """
    # 1. Search by data-test attribute (most reliable)
    elements = soup.select(f'[data-test="{data_test_attribute}"]')
    for element in elements:
        text = element.get_text(strip=True)
        numbers = re.findall(r"\d+", text)
        if numbers:
            return numbers[0]

    # 2. Search in elements containing specific keywords
    all_elements = soup.find_all(class_=re.compile("details-item-value|value"))
    for element in all_elements:
        text = element.get_text(strip=True).lower()
        if any(keyword in text for keyword in context_keywords):
            numbers = re.findall(r"\d+", text)
            if numbers:
                return numbers[0]

    # 3. Search in any element with text containing keywords
    for keyword in context_keywords:
        elements_with_text = soup.find_all(string=re.compile(keyword, re.IGNORECASE))
        for element in elements_with_text:
            text = element.get_text(strip=True).lower()
            numbers = re.findall(r"\d+", text)
            if numbers:
                return numbers[0]

    return default


def extract_business_type(url, soup):
    """
    Detect business type from multiple sources.

    Args:
        url: Property URL
        soup: BeautifulSoup object

    Returns:
        Business type: "Venta", "Arriendo", or "N/A"
    """
    operation_type = safe_extract(
        soup,
        [
            "[data-test='operation-type-value']",
            ".operation-type .place-features__values",
        ],
    )

    if "Venta" in operation_type:
        return "Venta"
    elif "Arriendo" in operation_type or "Renta" in operation_type:
        return "Arriendo"

    if "/venta/" in url.lower() or "venta" in url.lower():
        return "Venta"
    elif (
        "/arriendo/" in url.lower()
        or "arriendo" in url.lower()
        or "renta" in url.lower()
    ):
        return "Arriendo"

    page_text = soup.get_text().lower()
    if "venta" in page_text and "arriendo" not in page_text:
        return "Venta"
    elif "arriendo" in page_text or "renta" in page_text:
        return "Arriendo"

    return "N/A"


def detect_captcha(html):
    """Detect if page contains CAPTCHA."""
    soup = BeautifulSoup(html, "html.parser")
    page_text = soup.get_text().lower()

    from src.models.properati_scraper.config import CAPTCHA_INDICATORS

    return any(indicator.lower() in page_text for indicator in CAPTCHA_INDICATORS)
