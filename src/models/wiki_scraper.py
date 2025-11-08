from scraper_base import Scraper

class WikiScraper(Scraper):
    def __init__(self, base_url="https://en.wikipedia.org", endpoints=None) -> None:
        super().__init__(base_url=base_url, endpoints=endpoints or ["/wiki/Web_scraping"])

    def parse(self, html: str) -> dict:
        from bs4 import BeautifulSoup


        soup = BeautifulSoup(html, "html.parser")
        try:
            # Título: puede no existir en páginas atípicas
            title_tag = soup.find("h1", {"id": "firstHeading"})
            title = title_tag.text.strip() if title_tag and title_tag.text else ""

            # Contenido principal: asegurar que existe antes de buscar párrafos
            content = soup.find("div", {"class": "mw-parser-output"})
            if content:
                paragraphs = content.find_all("p")
                # Ignorar párrafos vacíos y limpiar texto
                text = "\n".join([para.get_text().strip() for para in paragraphs if para.get_text().strip()])
            else:
                text = ""

            return {"title": title, "content": text}
        except Exception as e:
            # Devolver estructura consistente y mensaje de error para depuración
            return {"title": "", "content": "", "error": str(e)}
