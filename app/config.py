from pathlib import Path


class Config(object):
    ROOT_PATH = Path(__file__).parent
    TESTING = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + ROOT_PATH.parent.joinpath('flask.db').as_posix()
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SERVER_NAME = 'menus.sralloza.es'
