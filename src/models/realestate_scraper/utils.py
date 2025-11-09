# realestate_scraper/utils.py
import unicodedata

def normalize_text(s: str) -> str:
    """Normaliza texto: minúsculas, sin acentos, sin espacios extra."""
    if not s:
        return ""
    s2 = s.lower().strip()
    s2 = unicodedata.normalize("NFKD", s2)
    s2 = "".join(ch for ch in s2 if not unicodedata.combining(ch))
    s2 = " ".join(s2.split())
    return s2
