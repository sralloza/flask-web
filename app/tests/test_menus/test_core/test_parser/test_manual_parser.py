import pytest
from bs4 import BeautifulSoup

from app.menus.core.exceptions import ParserError
from app.menus.core.parser.manual_parser import ManualParser
from app.tests.data.data import Paths


class TestManualParser:
    @pytest.mark.parametrize("data_path", Paths.not_html.value)
    def test_process_url_true(self, data_path):
        content = data_path.read_text(errors="ignore")
        assert ManualParser.process_text(None, content, "url")

    @pytest.mark.parametrize("data_path", Paths.html.value)
    def test_process_url_false(self, data_path):
        content = data_path.read_text(errors="ignore")
        with pytest.raises(ParserError):
            ManualParser.process_text(None, content, "url")

    @pytest.mark.parametrize("data_path", Paths.pdf.value)
    def test_detect_if_pdf_true(self, data_path):
        content = data_path.read_text(errors="ignore")
        manual_parser = ManualParser(BeautifulSoup(content, "html.parser"))
        assert manual_parser.detect_if_pdf()

    @pytest.mark.parametrize("data_path", Paths.not_pdf.value)
    def test_detect_if_pdf_false(self, data_path):
        content = data_path.read_text(errors="ignore")
        manual_parser = ManualParser(BeautifulSoup(content, "html.parser"))
        assert not manual_parser.detect_if_pdf()

    @pytest.mark.parametrize("data_path", Paths.photos.value)
    def test_detect_if_photo_true(self, data_path):
        content = data_path.read_text(errors="ignore")
        manual_parser = ManualParser(BeautifulSoup(content, "html.parser"))
        assert manual_parser.detect_if_photo()

    @pytest.mark.parametrize("data_path", Paths.not_photos.value)
    def test_detect_if_photo_false(self, data_path):
        content = data_path.read_text(errors="ignore")
        manual_parser = ManualParser(BeautifulSoup(content, "html.parser"))
        assert not manual_parser.detect_if_photo()
