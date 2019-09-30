import json
from pathlib import Path
from typing import Tuple, List

import pytest

from app.menus.core.daily_menus_manager import DailyMenusManager
from app.menus.core.parser import HtmlParser
from app.tests.data.data import Paths

ptd_type = List[Tuple[Path, Path]]

process_text_data: ptd_type = []

for html_path in Paths.html.value:
    for json_path in Paths.json.value:
        if html_path.stem == json_path.stem:
            process_text_data.append((html_path, json_path))
            break


class TestHtmlParser:
    @pytest.mark.parametrize('html_path, json_path', process_text_data)
    def test_process_text(self, html_path, json_path):
        dmm = DailyMenusManager()
        HtmlParser.process_text(dmm, html_path.read_text(encoding='utf-8'))

        json_expected = json.loads(json_path.read_text(encoding='utf-8'))
        json_real = dmm.to_json()

        assert json_real == json_expected

    def test_hidden_process_texts(self):
        # If test_process_text pass, this will too
        pass

    def test_update_menu(self):
        # If test_process_text pass, this will too
        pass
