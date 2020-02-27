import pytest

from app.tests.data.data import HtmlParserPaths


@pytest.fixture(scope="class")
def urls_json():
    json_data = HtmlParserPaths.urls_dict.value

    hole_data = {}
    for _, dict1 in json_data.items():
        for key2, value in dict1.items():
            hole_data[key2] = value

    yield hole_data


def name(path):
    return path.stem.replace(".html", "")


class TestJsonUrls:
    def test_pdfs(self, urls_json):
        for url in HtmlParserPaths.pdf.value:
            assert name(url) in urls_json

    def test_photos(self, urls_json):
        for url in HtmlParserPaths.photos.value:
            assert name(url) in urls_json

    def test_html(self, urls_json):
        for url in HtmlParserPaths.html.value:
            assert name(url) in urls_json

    def test_not_pdf(self, urls_json):
        for url in HtmlParserPaths.not_pdf.value:
            assert name(url) in urls_json

    def test_not_photos(self, urls_json):
        for url in HtmlParserPaths.not_photos.value:
            assert name(url) in urls_json

    def test_not_html(self, urls_json):
        for url in HtmlParserPaths.not_html.value:
            assert name(url) in urls_json
