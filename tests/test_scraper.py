import unittest
import tempfile
import os
import json
import requests

from scraper_base import Scraper


class MockResponse:
    def __init__(self, text='', status_code=200, raise_for_status_exc=None):
        self.text = text
        self.status_code = status_code
        self._raise_exc = raise_for_status_exc

    def raise_for_status(self):
        if self._raise_exc:
            raise self._raise_exc


class MockSession:
    def __init__(self, response=None, exc=None):
        self._response = response
        self._exc = exc

    def get(self, url, timeout=10):
        if self._exc:
            raise self._exc
        return self._response


class TestScraperBase(unittest.TestCase):
    def test_parse_raises_not_implemented(self):
        s = Scraper()
        with self.assertRaises(NotImplementedError):
            s.parse('<html></html>')

    def test_fetch_html_success(self):
        s = Scraper(base_url='http://example.com')
        s.session = MockSession(response=MockResponse(text='OK'))
        html = s.fetch_html('/path')
        self.assertEqual(html, 'OK')

    def test_fetch_html_request_exception(self):
        s = Scraper(base_url='http://example.com')
        s.session = MockSession(exc=requests.exceptions.RequestException('fail'))
        html = s.fetch_html('/path')
        self.assertEqual(html, '')

    def test_save_data_writes_file(self):
        s = Scraper()
        s.data = [{'a': 1, 'b': 'x'}]
        with tempfile.TemporaryDirectory() as td:
            filename = 'out.json'
            s.save_data(filename, folder=td)
            path = os.path.join(td, filename)
            self.assertTrue(os.path.exists(path))
            with open(path, 'r', encoding='utf-8') as f:
                content = json.load(f)
            self.assertEqual(content, s.data)

    def test_run_calls_parse_and_collects_data(self):
        # Crear una subclase que no haga peticiones de red
        class DummyScraper(Scraper):
            def __init__(self):
                super().__init__(base_url='', endpoints=['/a', '/b'])

            def fetch_html(self, endpoint):
                return '<html></html>'

            def parse(self, html):
                return {'ok': True}

        ds = DummyScraper()
        ds.run()
        # Debe haber añadido dos elementos (uno por cada endpoint)
        self.assertEqual(len(ds.data), 2)
        for item in ds.data:
            self.assertEqual(item, {'ok': True})


if __name__ == '__main__':
    unittest.main()
