class Config(object):
    DEBUG = False
    TESTING = False
    SERVER_NAME = 'localhost'
    PARSE_MAIN_WEB = False
    LAST_URL = 'https://www.residenciasantiago.es/2019/03/04/semana-del-5-al-11-de-marzo-2019/'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///flask.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class TestingConfig(Config):
    DEBUG = False
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///flask_tmp.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
