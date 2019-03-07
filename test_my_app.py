import pytest
from flask import url_for

from app import create_app


@pytest.fixture
def app():
    app = create_app(config_object='app.config.TestingConfig')
    return app


def test_index_ping(client):
    r_index = client.get(url_for('base.index', _external=True))
    assert r_index.status_code == 302
    assert r_index.location == url_for('base.menus', _external=True)


def test_menus_ping(client):
    r_menus = client.get(url_for('base.menus', _external=True))
    assert r_menus.status_code == 302
    assert 'residenciasantiago' in r_menus.location


def test_m_ping(client):
    assert client.get('m').location == url_for('base.menus', _external=True)


def test_aemet_ping(client):
    r_aemet = client.get(url_for('base.aemet', _external=True))
    assert r_aemet.status_code == 302
    assert 'aemet' in r_aemet.location
    assert 'prediccion' in r_aemet.location
    assert 'horas' in r_aemet.location
    assert 'tabla' in r_aemet.location
    assert 'valladolid' in r_aemet.location


def test_a_ping(client):
    assert client.get('a').location == url_for('base.aemet', _external=True)


def test_favicon_ping(client):
    r_favicon = client.get('favicon.ico')
    assert r_favicon.status_code == 302
    assert '/static/favicon.png' in r_favicon.location


def test_static_ping(client):
    assert client.get(url_for('static', filename='peter.pdf', _external=True)).status_code == 404
    assert client.get(url_for('static', filename='favicon.png', _external=True)).status_code == 200


def test_new_menus_ping(client):
    r_new_menus = client.get(url_for('new_menus.new_menus', _external=True))
    assert r_new_menus.status_code == 200
