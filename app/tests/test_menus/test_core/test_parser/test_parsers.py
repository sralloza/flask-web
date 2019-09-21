from collections import UserList
from unittest import mock

import pytest

from app.menus.core.parser import Parsers, ParserThread, ParserThreadList


class TestParserThread:
    def test_attributes(self):
        thread = ParserThread(None, None)
        assert hasattr(thread, 'url')
        assert hasattr(thread, 'dmm')
        assert hasattr(thread, 'retries')

    @mock.patch('app.menus.core.parser.logger')
    @mock.patch('app.menus.core.parser.Parsers')
    @mock.patch('app.menus.core.parser.requests.get')
    def test_run_without_errors(self, get_mock, parsers_mock, logger_mock):
        get_mock.return_value.text = 'text'
        parser = mock.MagicMock()
        parser.__name__ = 'mock-parser'
        parsers_mock.parsers = [parser] * 5
        dmm = mock.MagicMock()

        thread = ParserThread('url', dmm)
        thread.start()
        thread.join()

        parser.process_url.assert_called()
        assert parser.process_url.call_count == 1
        get_mock.assert_called_with('url')

        logger_mock.debug.assert_called()
        assert logger_mock.debug.call_count == 2
        logger_mock.info.assert_called_once()

    @mock.patch('app.menus.core.parser.logger')
    @mock.patch('app.menus.core.parser.Parsers')
    @mock.patch('app.menus.core.parser.requests.get')
    def test_run_with_some_errors(self, get_mock, parsers_mock, logger_mock):
        get_mock.return_value.text = 'text'
        parser = mock.MagicMock()
        parser.__name__ = 'mock-parser'
        parsers_mock.parsers = [parser] * 5
        dmm = mock.MagicMock()

        parser.process_url.side_effect = [ValueError, ValueError, True]

        thread = ParserThread('url', dmm)
        thread.start()
        thread.join()

        parser.process_url.assert_called()
        assert parser.process_url.call_count == 3
        get_mock.assert_called_with('url')
        logger_mock.debug.assert_called()
        assert logger_mock.debug.call_count == 4
        logger_mock.info.assert_called_once()
        logger_mock.exception.assert_called()
        assert logger_mock.exception.call_count == 2

    @mock.patch('app.menus.core.parser.logger')
    @mock.patch('app.menus.core.parser.Parsers')
    @mock.patch('app.menus.core.parser.requests.get')
    def test_run_with_fatal_error(self, get_mock, parsers_mock, logger_mock):
        get_mock.return_value.text = 'text'
        parser = mock.MagicMock()
        parser.__name__ = 'mock-parser'
        parsers_mock.parsers = [parser] * 5
        dmm = mock.MagicMock()

        parser.process_url.side_effect = ValueError

        thread = ParserThread('url', dmm)
        thread.start()
        thread.join()

        parser.process_url.assert_called()
        assert parser.process_url.call_count == 5
        get_mock.assert_called_with('url')

        logger_mock.debug.assert_called()
        assert logger_mock.debug.call_count == 6
        logger_mock.info.assert_not_called()
        logger_mock.exception.assert_called()
        assert logger_mock.exception.call_count == 5
        logger_mock.error.assert_called_once()


class TestParserList:
    @pytest.fixture
    def parser_thread_list(self):
        return ParserThreadList()

    def test_inherintance(self, parser_thread_list):
        assert isinstance(parser_thread_list, UserList)
        assert hasattr(parser_thread_list, '__getitem__')
        assert hasattr(parser_thread_list, '__setitem__')
        assert hasattr(parser_thread_list, '__delitem__')
        assert hasattr(parser_thread_list, '__len__')
        assert hasattr(parser_thread_list, '__iter__')

    @pytest.mark.parametrize('object', [ParserThread(None, None), ParserThread(None, None, None)])
    def test_append_valid(self, object, parser_thread_list):
        parser_thread_list.append(object)

    @pytest.mark.parametrize('object', ['a', 5, 1 + 3j, False, True])
    def test_append_invalid(self, object, parser_thread_list):
        with pytest.raises(TypeError):
            parser_thread_list.append(object)


class TestParsers:
    @mock.patch('app.menus.core.parser.ParserThread')
    @mock.patch('app.menus.core.parser.ParserThreadList.append')
    def test_parse(self, append_mock, thread_mock):
        url = mock.MagicMock()
        dmm = mock.MagicMock()
        Parsers.parse(url, dmm)

        thread_mock.assert_called_once()
        thread_mock.return_value.start.assert_called_once()
        append_mock.assert_called_once_with(thread_mock.return_value)

    @mock.patch('app.menus.core.parser.ParserThreadList.append')
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
