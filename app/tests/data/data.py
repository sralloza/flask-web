from enum import Enum
from pathlib import Path

from app.config import Config

web_data: Path = Config.TEST_DATA_PATH / 'web_data'
pdf_paths = list(web_data.rglob('1*.html'))
photos_paths = list(web_data.rglob('2*.html'))
html_paths = list(web_data.rglob('3*.html'))

menus_json: Path = Config.TEST_DATA_PATH / 'menus_json'
json_paths = list(menus_json.rglob('3*.json'))


class Paths(Enum):
    pdf = pdf_paths
    photos = photos_paths
    html = html_paths
    not_pdf = photos_paths + html_paths
    not_photos = pdf_paths + html_paths
    not_html = pdf_paths + photos_paths
    json = json_paths
