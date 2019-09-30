from collections import UserList
from unittest import mock

import pytest
from requests.exceptions import ConnectionError

from app.menus.core.parser import Parsers, ParserThread, ParserThreadList


class TestParserThread:
    def test_attributes(self):
        thread = ParserThread(None, None)
        assert hasattr(thread, "url")
        assert hasattr(thread, "dmm")
        assert hasattr(thread, "retries")

    @pytest.fixture
    def parser_mocks(self):
        logger_mock = mock.patch("app.menus.core.parser.logger", autospec=True).start()
        html = mock.patch("app.menus.core.parser.HtmlParser", autospec=True).start()
        manual = mock.patch("app.menus.core.parser.ManualParser", autospec=True).start()
        get = mock.patch("app.menus.core.parser.requests.get", autospec=True).start()

        parsers = mock.patch("app.menus.core.parser.Parsers").start()

        # In order of appearance in the real Parsers.parsers
        parsers.parsers = [html, manual]

        html.__name__ = "<HtmlParser Mocked>"
        manual.__name__ = "<ManualParser Mocked>"

        yield get, html, manual, logger_mock

        mock.patch.stopall()

    def test_run_without_errors(self, parser_mocks):
        get_mock, html_mock, manual_mock, logger_mock = parser_mocks

        get_mock.return_value.text = "text"
        dmm = mock.MagicMock()

        thread = ParserThread("url", dmm)
        thread.start()
        thread.join()

        # First parser is called
        html_mock.process_text.assert_called_once()

        # The rest of the parsers are not called
        manual_mock.process_text.assert_not_called()

        get_mock.assert_called_once_with("url")

        # Debug called 2 times (Starting and Trying)
        logger_mock.debug.assert_called()
        assert logger_mock.debug.call_count == 2

        # Info called 1 time (after HtmlParser success)
        logger_mock.info.assert_called_once()

        # Error called 0 times (no error)
        logger_mock.error.assert_not_called()

    def test_run_with_some_errors(self, parser_mocks):
        get_mock, html_mock, manual_mock, logger_mock = parser_mocks

        get_mock.return_value.text = "text"
        dmm = mock.MagicMock()

        # Simulate error in HtmlParser and no error in ManualParser
        html_mock.process_text.side_effect = ValueError
        manual_mock.process_text.return_value = True

        thread = ParserThread("url", dmm)
        thread.start()
        thread.join()

        # parser.process_text.assert_called()
        # assert parser.process_text.call_count == 3

        # Now, both parsers should have been called (due to error in HtmlParser)
        html_mock.process_text.assert_called_once()
        manual_mock.process_text.assert_called_once()

        get_mock.assert_called_once_with("url")

        # Debug called 3 times (1xStarting, 2xTrying with...)
        logger_mock.debug.assert_called()
        assert logger_mock.debug.call_count == 3

        # Info called 1 time (after ManualParser success)
        logger_mock.info.assert_called_once()

        # Exception called 1 time (after HtmlParser error)
        logger_mock.exception.assert_called()
        assert logger_mock.exception.call_count == 1

        # Error called 0 times (no error)
        logger_mock.error.assert_not_called()

    def test_run_with_fatal_error(self, parser_mocks):
        get_mock, html_mock, manual_mock, logger_mock = parser_mocks

        get_mock.return_value.text = "text"
        dmm = mock.MagicMock()

        # Simulate situation where HtmlParser and ManualParser
        # always raise ValueError
        html_mock.process_text.side_effect = ValueError
        manual_mock.process_text.side_effect = ValueError

        thread = ParserThread("url", dmm)
        thread.start()
        thread.join()

        # Both parsers should be called 1 times
        html_mock.process_text.assert_called_once()
        manual_mock.process_text.assert_called_once()

        get_mock.assert_called_once_with("url")

        # Logger called 63 times (1xStarting + 2xTrying)
        logger_mock.debug.assert_called()
        assert logger_mock.debug.call_count == 3

        # Info called 0 times (no success, only errors)
        logger_mock.info.assert_not_called()

        # Exception called 2 times (after call to each parser)
        logger_mock.exception.assert_called()
        assert logger_mock.exception.call_count == 2

        # Error called 1 time (at the end)
        logger_mock.error.assert_called_once()

    def test_run_with_one_error_in_request(self, parser_mocks):
        get_mock, html_mock, manual_mock, logger_mock = parser_mocks

        dmm = mock.MagicMock()

        # Simulate situation where requests.get returns one error
        foo_mock = mock.MagicMock()
        foo_mock.text = "text"
        get_mock.side_effect = [ConnectionError, foo_mock]

        thread = ParserThread("url", dmm)
        thread.start()
        thread.join()

        # First parser is called
        html_mock.process_text.assert_called_once()

        # The rest of the parsers are not called
        manual_mock.process_text.assert_not_called()

        # Get called 2 times (1 error)
        get_mock.assert_called_with("url")
        assert get_mock.call_count == 2

        # Debug called 2 times (Starting and Trying)
        logger_mock.debug.assert_called()
        assert logger_mock.debug.call_count == 2

        # Info called 1 time (after HtmlParser success)
        logger_mock.info.assert_called_once()

        # Error called 0 times (no error)
        logger_mock.error.assert_not_called()

    def test_run_with_three_error_in_request(self, parser_mocks):
        get_mock, html_mock, manual_mock, logger_mock = parser_mocks

        dmm = mock.MagicMock()

        # Simulate situation where requests.get returns one error
        foo_mock = mock.MagicMock()
        foo_mock.text = "text"
        get_mock.side_effect = [
            ConnectionError,
            ConnectionError,
            ConnectionError,
            foo_mock,
        ]

        thread = ParserThread("url", dmm)
        thread.start()
        thread.join()

        # First parser is called
        html_mock.process_text.assert_called_once()

        # The rest of the parsers are not called
        manual_mock.process_text.assert_not_called()

        # Get called 4 times (3 error)
        get_mock.assert_called_with("url")
        assert get_mock.call_count == 4

        # Debug called 2 times (Starting and Trying)
        logger_mock.debug.assert_called()
        assert logger_mock.debug.call_count == 2

        # Info called 1 time (after HtmlParser success)
        logger_mock.info.assert_called_once()

        # Error called 0 times (no error)
        logger_mock.error.assert_not_called()

    def test_run_with_fatal_error_in_request(self, parser_mocks):
        get_mock, html_mock, manual_mock, logger_mock = parser_mocks

        dmm = mock.MagicMock()

        # Simulate situation where requests.get returns one error
        foo_mock = mock.MagicMock()
        foo_mock.text = "text"
        get_mock.side_effect = ConnectionError

        thread = ParserThread("url", dmm)
        thread.start()
        thread.join()

        # None of the parsers called due to fatal error
        html_mock.process_text.assert_not_called()
        manual_mock.process_text.assert_not_called()

        # Get called 5 times (5 error)
        get_mock.assert_called_with("url")
        assert get_mock.call_count == 5

        # Debug called 1 times (Starting)
        logger_mock.debug.assert_called_once()

        # Info called 0 time (no success)
        logger_mock.info.assert_not_called()

        # Error called 1 times (fatal error)
        logger_mock.error.assert_called_once()

    def test_run_with_seven_error_in_request_with_ten_retries(self, parser_mocks):
        get_mock, html_mock, manual_mock, logger_mock = parser_mocks

        dmm = mock.MagicMock()

        # Simulate situation where requests.get returns one error
        foo_mock = mock.MagicMock()
        foo_mock.text = "text"
        get_mock.side_effect = [
            ConnectionError,
            ConnectionError,
            ConnectionError,
            ConnectionError,
            ConnectionError,
            ConnectionError,
            ConnectionError,
            foo_mock,
        ]

        thread = ParserThread("url", dmm, retries=10)
        thread.start()
        thread.join()

        # First parser is called
        html_mock.process_text.assert_called_once()

        # The rest of the parsers are not called
        manual_mock.process_text.assert_not_called()

        # Get called 8 times (7 error)
        get_mock.assert_called_with("url")
        assert get_mock.call_count == 8

        # Debug called 2 times (Starting and Trying)
        logger_mock.debug.assert_called()
        assert logger_mock.debug.call_count == 2

        # Info called 1 time (after HtmlParser success)
        logger_mock.info.assert_called_once()

        # Error called 0 times (no error)
        logger_mock.error.assert_not_called()


class TestParserList:
    @pytest.fixture
    def parser_thread_list(self):
        return ParserThreadList()

    def test_inherintance(self, parser_thread_list):
        assert isinstance(parser_thread_list, UserList)
        assert hasattr(parser_thread_list, "__getitem__")
        assert hasattr(parser_thread_list, "__setitem__")
        assert hasattr(parser_thread_list, "__delitem__")
        assert hasattr(parser_thread_list, "__len__")
        assert hasattr(parser_thread_list, "__iter__")

    @pytest.mark.parametrize(
        "object", [ParserThread(None, None), ParserThread(None, None, None)]
    )
    def test_append_valid(self, object, parser_thread_list):
        parser_thread_list.append(object)

    @pytest.mark.parametrize("object", ["a", 5, 1 + 3j, False, True])
    def test_append_invalid(self, object, parser_thread_list):
        with pytest.raises(TypeError):
            parser_thread_list.append(object)


class TestParsers:
    @mock.patch("app.menus.core.parser.ParserThread")
    @mock.patch("app.menus.core.parser.ParserThreadList.append")
    def test_parse(self, append_mock, thread_mock):
        url = mock.MagicMock()
        dmm = mock.MagicMock()
        Parsers.parse(url, dmm)

        thread_mock.assert_called_once()
        thread_mock.return_value.start.assert_called_once()
        append_mock.assert_called_once_with(thread_mock.return_value)

    @mock.patch("app.menus.core.parser.ParserThreadList.append")
    def test_append(self, append_mock):
        thread = ParserThread(None, None)
        Parsers._append(thread)
        append_mock.assert_called_with(thread)

    def test_join(self):
        thread_mock = mock.MagicMock()
        Parsers._threads = [thread_mock] * 10
        Parsers.join()

        thread_mock.join.assert_called_with()
        assert thread_mock.join.call_count == 10
