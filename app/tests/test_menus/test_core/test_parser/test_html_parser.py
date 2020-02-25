import json
from pathlib import Path
from typing import Tuple, List

import pytest

from app.menus.core.daily_menus_manager import DailyMenusManager
from app.menus.core.parser import HtmlParser
from app.tests.data.data import HtmlParserPaths

ptd_type = List[Tuple[Path, Path]]

process_text_data: ptd_type = []

for html_path in HtmlParserPaths.html.value:
    for json_path in HtmlParserPaths.json.value:
        # Due to naming convention
        if html_path.stem == json_path.stem + ".html":
            process_text_data.append(
                (
                    html_path,
                    json_path,
                    HtmlParserPaths.urls_dict.value["html"].get(json_path.stem, None),
                )
            )
            break


def test_correct_text_data():
    assert process_text_data


class TestHtmlParser:
    @pytest.mark.parametrize("html_path, json_path, url", process_text_data)
    def test_process_text(self, html_path, json_path, url):
        dmm = DailyMenusManager()
        HtmlParser.process_text(dmm, html_path.read_text(encoding="utf-8"), url)

        json_expected = json.loads(json_path.read_text(encoding="utf-8"))
        json_real = dmm.to_json()

        assert json_real == json_expected

    def test_hidden_process_texts(self):
        # If test_process_text pass, this will too
        pass

    def test_update_menu(self):
        # If test_process_text pass, this will too
        pass
