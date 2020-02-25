from enum import Enum
from pathlib import Path
import json
from app.config import Config


class TestPaths(Enum):
    filter_data = Config.TEST_DATA_PATH / "menus.core.filter_data"
    html_parser = Config.TEST_DATA_PATH / "menus.core.parser.HtmlParser.parse"
    get_menus_urls = Config.TEST_DATA_PATH / "menus.core.utils.get_menus_urls"


_web_data_folder = TestPaths.html_parser.value / "input"
_pdf_paths = list(_web_data_folder.joinpath("pdf").rglob("*.html.data"))
_photos_paths = list(_web_data_folder.joinpath("photos").rglob("*.html.data"))
_html_paths = list(_web_data_folder.joinpath("html").rglob("*.html.data"))

_menus_json = TestPaths.html_parser.value / "output"
_json_paths = list(_menus_json.joinpath("html").rglob("*.json"))

_urls_dict = json.loads(
    _web_data_folder.joinpath("urls.json").read_text(encoding="utf-8")
)


class HtmlParserPaths(Enum):
    pdf = _pdf_paths
    photos = _photos_paths
    html = _html_paths
    not_pdf = _photos_paths + _html_paths
    not_photos = _pdf_paths + _html_paths
    not_html = _pdf_paths + _photos_paths
    json = _json_paths
    urls_dict = _urls_dict


class FilterDataPaths(Enum):
    inputs = TestPaths.filter_data.value.joinpath("input").rglob("*.txt.data")
    outputs = TestPaths.filter_data.value.joinpath("output").rglob("*.txt.data")
