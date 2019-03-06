import pytest
from flask import url_for, current_app

from my_app import create_app


@pytest.fixture
def app():
    app = create_app(config_object='config.TestingConfig')
    return app


def test_api_ping(client):
    # res = client.get(url_for('index'))
    # assert res == 0

     print(current_app.url_map)