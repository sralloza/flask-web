import os
from unittest import mock

import pytest

from app import create_app, db
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
        db.create_all()
        yield testing_client  # this is where the testing happens!
        db.drop_all()


@pytest.fixture(scope="function")
def reset_database():
    config_mock = mock.patch("app.menus.models.Config", autospec=True).start()

    # todo random temp file
    config_mock.DATABASE_PATH = TestingConfig.DATABASE_PATH

    yield TestingConfig.DATABASE_PATH

    mock.patch.stopall()

    try:
        os.remove(TestingConfig.DATABASE_PATH)
    except FileNotFoundError:
        pass
