"""This module contains the config for the application.
There is a main class (`Config`), and the rest are subclasses of it.
The second class is `TestingConfig`, desinged to be used during tests.
"""
import platform
from pathlib import Path


class Config:
    """General config class."""
    ROOT_PATH: Path = Path(__file__).parent
    TEST_DATA_PATH: Path = ROOT_PATH / "tests" / "data"
    TESTING: bool = False
    DATABASE_PATH: Path = ROOT_PATH.parent.joinpath("flask.db")
    IS_LINUX: bool = platform.system() == "Linux"
    BASE_RESIDENCE_URL: str = "https://www.residenciasantiago.es"
    TOKEN_FILE_PATH = ROOT_PATH / "VALID_TOKENS"
    OFFLINE = False


class TestingConfig(Config):
    """Config class to use during tests."""
    TESTING: bool = True
    DATABASE_PATH: Path = Path(Config.DATABASE_PATH).with_name("test-flask.db")
    SERVER_NAME: str = "menus.sralloza.es"
