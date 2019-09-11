import logging
from pathlib import Path

from flask import Flask
from flask_bootstrap import Bootstrap

from .base import base_blueprint
from .menus import menus_blueprint
from .menus.models import db

logging.basicConfig(
    filename=Path(__file__).parent.parent / 'flask-app.log',
    level=logging.DEBUG,
    format='%(asctime)s] %(levelname)s - %(name)s:%(lineno)s - %(message)s')

werkzeug = logging.getLogger('werkzeug')
werkzeug.handlers = []
werkzeug_handler = logging.FileHandler(
    Path(__file__).parent.parent / 'flask-access.log',
    encoding='utf-8')
werkzeug_handler.setFormatter(logging.Formatter(fmt='%(asctime)s] %(levelname)s - %(message)s'))
werkzeug.addHandler(werkzeug_handler)


def create_app(config_filename=None, config_object=None, settings_override=None):
    flask_app = Flask(__name__)

    if config_filename:
        flask_app.config.from_pyfile(config_filename)
    elif config_object:
        flask_app.config.from_object(config_object)
    elif settings_override:
        flask_app.config.from_json(settings_override)
    else:
        raise RuntimeError('Select config source (file or object)')

    db.init_app(flask_app)

    Bootstrap(flask_app)
    flask_app.register_blueprint(base_blueprint)
    flask_app.register_blueprint(menus_blueprint)

    db.create_all(app=flask_app)

    return flask_app


app = create_app(config_object='app.config.Config')
