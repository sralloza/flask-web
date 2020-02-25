from enum import Enum
from pathlib import Path
import json
from app.config import Config


class TestPaths(Enum):
    filter_data = Config.TEST_DATA_PATH / "menus.core.filter_data"
    html_parser = Config.TEST_DATA_PATH / "menus.core.parser.HtmlParser.parse"
    get_menus_urls = Config.TEST_DATA_PATH / "menus.core.utils.get_menus_urls"


web_data_folder = TestPaths.html_parser.value / "input"
pdf_paths = list(web_data_folder.joinpath("pdf").rglob("*.html.data"))
photos_paths = list(web_data_folder.joinpath("photos").rglob("*.html.data"))
html_paths = list(web_data_folder.joinpath("html").rglob("*.html.data"))

menus_json = TestPaths.html_parser.value / "output"
json_paths = list(menus_json.joinpath("html").rglob("*.json"))

urls_dict = json.loads(web_data_folder.joinpath("urls.json").read_text(encoding="utf-8"))


class HtmlParserPaths(Enum):
    pdf = pdf_paths
    photos = photos_paths
    html = html_paths
    not_pdf = photos_paths + html_paths
    not_photos = pdf_paths + html_paths
    not_html = pdf_paths + photos_paths
    json = json_paths
    urls_dict = urls_dict


class FilterDataPaths(Enum):
    inputs = TestPaths.filter_data.value.joinpath("input").rglob("*.txt.data")
    outputs = TestPaths.filter_data.value.joinpath("output").rglob("*.txt.data")
