import pytest

from app.tests.data.data import ParserPaths


@pytest.fixture(scope="class")
def urls_json_sep():
    json_data = ParserPaths.urls_dict.value

    yield json_data


@pytest.fixture(scope="class")
def urls_json(urls_json_sep):
    hole_data = {}
    for _, dict1 in urls_json_sep.items():
        for key2, value in dict1.items():
            hole_data[key2] = value
    yield hole_data


def name(path):
    return path.stem.replace(".html", "")


class TestJsonUrls:
    def test_pdfs(self, urls_json_sep):
        for url in ParserPaths.pdf.value:
            assert name(url) in urls_json_sep["pdf"]

    def test_photos(self, urls_json_sep):
        for url in ParserPaths.photos.value:
            assert name(url) in urls_json_sep["photos"]

    def test_html(self, urls_json_sep):
        for url in ParserPaths.html.value:
            assert name(url) in urls_json_sep["html"]

    def test_not_pdf(self, urls_json):
        for url in ParserPaths.not_pdf.value:
            assert name(url) in urls_json

    def test_not_photos(self, urls_json):
        for url in ParserPaths.not_photos.value:
            assert name(url) in urls_json

    def test_not_html(self, urls_json):
        for url in ParserPaths.not_html.value:
            assert name(url) in urls_json
