import logging

from flask import Flask
from flask_bootstrap import Bootstrap

from .base import blue
from .new_menus import new_menus
from .new_menus.models import db

logging.basicConfig(filename='flask_app.log', level=logging.DEBUG,
                    format='%(asctime)s] %(levelname)s - %(module)s:%(lineno)s - %(message)s')

werkzeug = logging.getLogger('werkzeug')
werkzeug.handlers = []
werkzeug_handler = logging.FileHandler('flask-access.log', encoding='utf-8')
werkzeug_handler.setFormatter(logging.Formatter(fmt='%(asctime)s] %(levelname)s - %(message)s'))
werkzeug.addHandler(werkzeug_handler)

def create_app(config_filename=None, config_object=None, settings_override=None):
    flask_app = Flask(__name__)

    db.init_app(flask_app)
    Bootstrap(flask_app)

    if config_filename:
        flask_app.config.from_pyfile(config_filename)
    elif config_object:
        flask_app.config.from_object(config_object)
    elif settings_override:
        flask_app.config.from_json(settings_override)
    else:
        raise RuntimeError('Select config source (file or object)')

    flask_app.register_blueprint(blue)
    flask_app.register_blueprint(new_menus)
    return flask_app


app = create_app(config_object='app.config.Config')
