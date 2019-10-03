import platform
from pathlib import Path


class Config(object):
    ROOT_PATH = Path(__file__).parent
    TEST_DATA_PATH = ROOT_PATH / 'tests' / 'data'
    TESTING = False
    DATABASE_PATH = ROOT_PATH.parent.joinpath('flask.db').as_posix()
    IS_LINUX = platform.system() == 'Linux'
    BASE_RESIDENCE_URL = 'https://www.residenciasantiago.es'


class TestingConfig(Config):
    TESTING = True
    DATABASE_PATH = Path(Config.DATABASE_PATH).with_name('test-flask.db').as_posix()
    SERVER_NAME = 'menus.sralloza.es'
