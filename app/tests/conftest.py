import pytest

from app import create_app, db


@pytest.fixture(scope='session', autouse=True)
def app():
    app = create_app(config_object='app.config.TestingConfig')
    return app


@pytest.fixture(scope='module')
def client(app):
    # Flask provides a way to test your application by exposing the Werkzeug
    # test Client and handling the context locals for you.
    testing_client = app.test_client()

    with app.app_context():
        db.create_all()
        yield testing_client  # this is where the testing happens!
        db.drop_all()
