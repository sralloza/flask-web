import pytest
from flask import url_for

from app import create_app


@pytest.fixture
def app():
    app = create_app(config_object='app.config.TestingConfig')
    return app


def test_api_ping(client):
    assert client.get(url_for('base.index', _external=True)).status_code == 302
    assert client.get(url_for('base.menus', _external=True)).status_code == 302
    assert client.get(url_for('base.aemet', _external=True)).status_code == 302
    assert client.get(url_for('static', filename='peter.pdf', _external=True)).status_code == 404
