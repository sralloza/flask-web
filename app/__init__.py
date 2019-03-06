from flask import Flask

from .new_menus import new_menus
from .base import blue


def create_app(config_filename=None, config_object=None):
    flask_app = Flask(__name__)

    if config_filename:
        flask_app.config.from_pyfile(config_filename)
    elif config_object:
        flask_app.config.from_object(config_object)
    else:
        raise RuntimeError('Select config source (file or object)')

    # flask_app.app_context().push()
    flask_app.register_blueprint(blue)
    flask_app.register_blueprint(new_menus)
    return flask_app


app = create_app(config_object='app.config.Config')

