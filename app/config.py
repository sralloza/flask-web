import platform
from pathlib import Path


class Config(object):
    ROOT_PATH: Path = Path(__file__).parent
    TEST_DATA_PATH: Path = ROOT_PATH / "tests" / "data"
    TESTING: bool = False
    DATABASE_PATH: Path = ROOT_PATH.parent.joinpath("flask.db")
    IS_LINUX: bool = platform.system() == "Linux"
    BASE_RESIDENCE_URL: str = "https://www.residenciasantiago.es"


class TestingConfig(Config):
    TESTING: bool = True
    DATABASE_PATH: Path = Path(Config.DATABASE_PATH).with_name("test-flask.db")
    SERVER_NAME: str = "menus.sralloza.es"
