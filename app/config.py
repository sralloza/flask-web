class Config(object):
    DEBUG = False
    TESTING = False
    PARSE_MAIN_WEB = False
    LAST_URL = 'https://www.residenciasantiago.es/2019/03/04/semana-del-5-al-11-de-marzo-2019/'


class TestingConfig(Config):
    DEBUG = False
    TESTING = True
