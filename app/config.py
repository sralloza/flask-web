from pathlib import Path


class Config(object):
    ROOT_PATH = Path(__file__).parent
    TESTING = False
    DATABASE_PATH = ROOT_PATH.parent.joinpath('flask.db').as_posix()
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + DATABASE_PATH
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class TestingConfig(Config):
    TESTING = True
    DATABASE_PATH = ':memory:'
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SERVER_NAME = 'menus.sralloza.es'
