"""Testing configuration for pytest."""

import pytest
from flask.globals import current_app

from app import create_app
from app.config import TestingConfig


@pytest.fixture(scope="session", autouse=True)
def app():
    """Creates the application."""
    return create_app(config_object="app.config.TestingConfig")


@pytest.fixture(scope="module")
def client(app):
    """Creates the client to simulate a real client."""
    # Flask provides a way to test your application by exposing the Werkzeug
    # test Client and handling the context locals for you.
    testing_client = app.test_client()

    with app.app_context():
        # Check if DATABASE_PATH config is TestingConfig.DATABASE_PATH
        assert current_app.config["DATABASE_PATH"] == TestingConfig.DATABASE_PATH

        yield testing_client  # this is where the testing happens!


@pytest.fixture(scope="function", autouse=True)
def remove_testing_database():
    """Removes the testing database."""
    yield

    if TestingConfig.DATABASE_PATH.is_file():
        TestingConfig.DATABASE_PATH.unlink()
