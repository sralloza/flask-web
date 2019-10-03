import os
import sqlite3
from unittest import mock

import pytest
from flask.globals import current_app

from app import create_app
from app.config import TestingConfig


@pytest.fixture(scope="session", autouse=True)
def app():
    app = create_app(config_object="app.config.TestingConfig")
    return app


@pytest.fixture(scope="module")
def client(app):
    # Flask provides a way to test your application by exposing the Werkzeug
    # test Client and handling the context locals for you.
    testing_client = app.test_client()

    with app.app_context():
        yield testing_client  # this is where the testing happens!


@pytest.fixture(scope="function")
def reset_database(client):
    # TODO: random temp file
    connection = sqlite3.connect(current_app.config["DATABASE_PATH"])
    cursor = connection.cursor()
    cursor.execute("DROP TABLE IF EXISTS 'update_control'")
    cursor.execute("DROP TABLE IF EXISTS 'daily_menus'")
    connection.commit()
    connection.close()
    yield
