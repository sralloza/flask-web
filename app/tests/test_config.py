import platform
from pathlib import Path

from app.config import Config, TestingConfig


class TestConfig:
    def test_root_path(self):
        assert hasattr(Config, "ROOT_PATH")
        assert isinstance(Config.ROOT_PATH, Path)

    def test_test_data_path(self):
        assert hasattr(Config, "TEST_DATA_PATH")
        assert isinstance(Config.TEST_DATA_PATH, Path)
        assert "tests" in Config.TEST_DATA_PATH.as_posix()
        assert "data" in Config.TEST_DATA_PATH.as_posix()

    def test_testing(self):
        assert hasattr(Config, "TESTING")
        assert isinstance(Config.TESTING, bool)
        assert Config.TESTING is False

    def test_database_path(self):
        assert hasattr(Config, "DATABASE_PATH")
        assert isinstance(Config.DATABASE_PATH, Path)
        assert "flask.db" in Config.DATABASE_PATH.as_posix()

    def test_is_linux(self):
        assert hasattr(Config, "IS_LINUX")
        assert isinstance(Config.IS_LINUX, bool)
        assert Config.IS_LINUX == (platform.system()[0] == "L")

    def test_token_file_path(self):
        assert hasattr(Config, "TOKEN_FILE_PATH")
        assert isinstance(Config.TOKEN_FILE_PATH, Path)
        assert "VALID_TOKENS" in Config.TOKEN_FILE_PATH.as_posix()

    def test_offline(self):
        assert hasattr(Config, "OFFLINE")
        assert isinstance(Config.OFFLINE, bool)

    def test_admin_email(self):
        assert hasattr(Config, "ADMIN_EMAIL")
        assert isinstance(Config.ADMIN_EMAIL, str)


class TestTestingConfig:
    def test_inherintance(self):
        assert issubclass(TestingConfig, Config)

    def test_testing(self):
        assert hasattr(TestingConfig, "TESTING")
        assert isinstance(TestingConfig.TESTING, bool)
        assert TestingConfig.TESTING is True

    def test_database_path(self):
        assert hasattr(TestingConfig, "DATABASE_PATH")
        assert isinstance(TestingConfig.DATABASE_PATH, Path)
        assert "test-flask.db" in TestingConfig.DATABASE_PATH.as_posix()

    def test_server_name(self):
        assert hasattr(TestingConfig, "SERVER_NAME")
        assert isinstance(TestingConfig.SERVER_NAME, str)
