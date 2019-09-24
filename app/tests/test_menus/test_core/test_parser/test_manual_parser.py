from enum import Enum
from pathlib import Path

import pytest
from bs4 import BeautifulSoup

from app.config import Config
from app.menus.core.exceptions import ParserError
from app.menus.core.parser.manual_parser import ManualParser

# test data:
# pdf: 11,12
# photos: 21
# html: 31,32,33

manual_parser_data: Path = Config.TEST_DATA_PATH / 'parser_data' / 'manual_parser'
pdf_paths = [manual_parser_data / '11.html', manual_parser_data / '12.html']
photos_paths = [manual_parser_data / '21.html']
html_paths = [manual_parser_data / '31.html', manual_parser_data / '32.html',
              manual_parser_data / '33.html']


class Paths(Enum):
    pdf = pdf_paths
    photos = photos_paths
    html = html_paths
    not_pdf = photos_paths + html_paths
    not_photos = pdf_paths + html_paths
    not_html = pdf_paths + photos_paths


# TODO: add more test data for situations where ManualParser is useless

class TestManualParser:

    @pytest.mark.parametrize('data_path', Paths.not_html.value)
    def test_process_url_true(self, data_path):
        content = data_path.read_text(errors='ignore')
        assert ManualParser.process_text(None, content)

    @pytest.mark.parametrize('data_path', Paths.html.value)
    def test_process_url_false(self, data_path):
        content = data_path.read_text(errors='ignore')
        with pytest.raises(ParserError):
            ManualParser.process_text(None, content)

    @pytest.mark.parametrize('data_path', Paths.pdf.value)
    def test_detect_if_pdf_true(self, data_path):
        content = data_path.read_text(errors='ignore')
        manual_parser = ManualParser(BeautifulSoup(content, 'html.parser'))
        assert manual_parser.detect_if_pdf()

    @pytest.mark.parametrize('data_path', Paths.not_pdf.value)
    def test_detect_if_pdf_false(self, data_path):
        content = data_path.read_text(errors='ignore')
        manual_parser = ManualParser(BeautifulSoup(content, 'html.parser'))
        assert not manual_parser.detect_if_pdf()

    @pytest.mark.parametrize('data_path', Paths.photos.value)
    def test_detect_if_photo_true(self, data_path):
        content = data_path.read_text(errors='ignore')
        manual_parser = ManualParser(BeautifulSoup(content, 'html.parser'))
        assert manual_parser.detect_if_photo()

    @pytest.mark.parametrize('data_path', Paths.not_photos.value)
    def test_detect_if_photo_false(self, data_path):
        content = data_path.read_text(errors='ignore')
        manual_parser = ManualParser(BeautifulSoup(content, 'html.parser'))
        assert not manual_parser.detect_if_photo()
