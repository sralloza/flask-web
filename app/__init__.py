import logging
from pathlib import Path
from platform import system

from flask import Flask
from flask_bootstrap import Bootstrap

from .base import base_blueprint
from .menus import menus_blueprint

logging.basicConfig(
    filename=Path(__file__).parent.parent / "flask-app.log",
    level=logging.DEBUG,
    format="[%(asctime)s] %(levelname)s - %(name)s:%(lineno)s - %(message)s",
)

werkzeug = logging.getLogger("werkzeug")
werkzeug.handlers = []

if system() != "Linux":
    werkzeug_handler = logging.FileHandler(
        Path(__file__).parent.parent / "flask-access.log", encoding="utf-8"
    )
    werkzeug_handler.setFormatter(
        logging.Formatter(fmt="%(asctime)s] %(levelname)s - %(message)s")
    )
    werkzeug.addHandler(werkzeug_handler)


def create_app(config_object):
    flask_app = Flask(__name__)

    flask_app.config.from_object(config_object)

    Bootstrap(flask_app)
    flask_app.register_blueprint(base_blueprint)
    flask_app.register_blueprint(menus_blueprint)

    return flask_app


app = create_app(config_object="app.config.Config")
