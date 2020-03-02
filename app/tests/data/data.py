from enum import Enum
from pathlib import Path
import json
from app.config import Config


class TestPaths(Enum):
    filter_data = Config.TEST_DATA_PATH / "menus.core.filter_data"
    html_parser = Config.TEST_DATA_PATH / "menus.core.parser.HtmlParser.parse"
    get_menus_urls = Config.TEST_DATA_PATH / "menus.core.utils.get_menus_urls"


_web_data_folder = TestPaths.html_parser.value / "input"
_pdf_paths = tuple(sorted(_web_data_folder.joinpath("pdf").rglob("*.html.data")))
_photos_paths = tuple(sorted(_web_data_folder.joinpath("photos").rglob("*.html.data")))
_html_paths = tuple(sorted(_web_data_folder.joinpath("html").rglob("*.html.data")))

_menus_json = TestPaths.html_parser.value / "output"
_json_paths = tuple(sorted(_menus_json.joinpath("html").rglob("*.json")))

_urls_dict = json.loads(
    _web_data_folder.joinpath("urls.json").read_text(encoding="utf-8")
)


class ParserPaths(Enum):
    pdf = _pdf_paths
    photos = _photos_paths
    html = _html_paths
    not_pdf = _photos_paths + _html_paths
    not_photos = _pdf_paths + _html_paths
    not_html = _pdf_paths + _photos_paths
    json = _json_paths
    urls_dict = _urls_dict


class FilterDataPaths(Enum):
    _inputs = TestPaths.filter_data.value.joinpath("input").rglob("*.txt.data")
    inputs = tuple(sorted(_inputs))
    _outputs = TestPaths.filter_data.value.joinpath("output").rglob("*.txt.data")
    outputs = tuple(sorted(_outputs))


class GetMenusUrlsDataPaths(Enum):
    _inputs = TestPaths.get_menus_urls.value.joinpath("input").rglob("*.html.data")
    inputs = tuple(sorted(_inputs))
    _outputs = TestPaths.get_menus_urls.value.joinpath("output").rglob("*.json")
    outputs = tuple(sorted(_outputs))
    _invalid = TestPaths.get_menus_urls.value.joinpath("invalid").rglob("*.html.data")
    invalid = tuple(_invalid)[0]
