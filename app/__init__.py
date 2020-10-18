import logging
from pathlib import Path
from platform import system
from random import choice
from string import ascii_letters

from flask import Flask
from flask_bootstrap import Bootstrap

from .base import base_blueprint
from .base.routes import after_request, before_request
from .menus import menus_blueprint

logging.basicConfig(
    filename=Path(__file__).parent.parent / "flask-app.log",
    level=logging.DEBUG,
    format="[%(asctime)s] %(levelname)s - %(threadName)s.%(name)s:%(lineno)s - %(message)s",
)

werkzeug = logging.getLogger("werkzeug")
werkzeug.setLevel(logging.INFO)
werkzeug.propagate = False
werkzeug.handlers = []

if system() != "Linux":
    werkzeug_handler = logging.FileHandler(
        Path(__file__).parent.parent / "flask-access.log", encoding="utf-8"
    )
    werkzeug_handler.setFormatter(
        logging.Formatter(fmt="%(asctime)s] %(levelname)s - %(message)s")
    )
    werkzeug_handler.setLevel(logging.INFO)
    werkzeug.addHandler(werkzeug_handler)


def create_app(config_object):
    flask_app = Flask(__name__)

    flask_app.config.from_object(config_object)

    Bootstrap(flask_app)
    flask_app.register_blueprint(base_blueprint)
    flask_app.register_blueprint(menus_blueprint)

    flask_app.after_request(after_request)
    flask_app.before_request(before_request)

    flask_app.secret_key = "".join(choice(ascii_letters) for _ in range(16))
    return flask_app


def get_version():
    path = Path(__file__).with_name("VERSION")
    return path.read_text().strip()


app = create_app(config_object="app.config.Config")
