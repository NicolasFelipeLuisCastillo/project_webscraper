import unittest
from wiki_scraper import WikiScraper


class TestWikiScraperParse(unittest.TestCase):
    def setUp(self):
        self.scraper = WikiScraper()

    def test_parse_valid_html(self):
        html = '''
        <html><head><title>Test</title></head>
        <body>
        <h1 id="firstHeading">Test Title</h1>
        <div class="mw-parser-output">
            <p>First paragraph.</p>
            <p>Second paragraph.</p>
        </div>
        </body></html>
        '''
        result = self.scraper.parse(html)
        self.assertIsInstance(result, dict)
        self.assertEqual(result.get("title"), "Test Title")
        self.assertEqual(result.get("content"), "First paragraph.\nSecond paragraph.")

    def test_parse_missing_title(self):
        html = '''
        <html><body>
        <div class="mw-parser-output"><p>Only paragraph.</p></div>
        </body></html>
        '''
        result = self.scraper.parse(html)
        self.assertEqual(result.get("title"), "")
        self.assertEqual(result.get("content"), "Only paragraph.")

    def test_parse_missing_content(self):
        html = '<html><body><h1 id="firstHeading">Title Only</h1></body></html>'
        result = self.scraper.parse(html)
        self.assertEqual(result.get("title"), "Title Only")
        self.assertEqual(result.get("content"), "")

    def test_parse_none_input_returns_error(self):
        result = self.scraper.parse(None)
        # Esperamos un diccionario con clave 'error' y valores vacíos para title/content
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)
        self.assertEqual(result.get("title"), "")
        self.assertEqual(result.get("content"), "")


if __name__ == "__main__":
    unittest.main()
