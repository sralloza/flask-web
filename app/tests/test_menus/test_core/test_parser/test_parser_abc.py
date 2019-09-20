import pytest

from app.menus.core.parser import BaseParser


class TestBaseParser:
    def test_new(self):
        with pytest.raises(TypeError, match="Can't instantiate abstract class "
                                            "BaseParser with abstract methods process_url"):
            BaseParser()

    def test_process_url(self):
        with pytest.raises(NotImplementedError):
            BaseParser.process_url('', '')
