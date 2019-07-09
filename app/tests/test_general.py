import pytest
from flask import url_for
from flask.testing import FlaskClient


@pytest.mark.skip(reason='old')
def test_useragent_block(client: FlaskClient):
    index_url = url_for('base.index', _external=True)

    assert client.get(index_url, headers={
        'User-Agent': 'python-requests/2.21.0', 'Accept-Encoding': 'gzip, deflate',
        'Accept': '*/*', 'Connection': 'keep-alive'}).status_code == 401

    assert client.get(index_url, headers={
        'User-Agent': 'Rift/2.0', 'Accept-Encoding': 'gzip, deflate',
        'Accept': '*/*', 'Connection': 'keep-alive'}).status_code == 401


@pytest.mark.skip(reason='old')
def test_menus_ping(client):
    r_menus = client.get(url_for('base.menus', _external=True))
    assert r_menus.status_code == 302
    assert 'residenciasantiago' in r_menus.location


@pytest.mark.skip(reason='old')
def test_m_ping(client):
    assert client.get('m').location == url_for('base.menus', _external=True)


@pytest.mark.skip(reason='old')
def test_aemet_ping(client):
    r_aemet = client.get(url_for('base.aemet', _external=True))
    assert r_aemet.status_code == 302
    assert 'aemet' in r_aemet.location
    assert 'prediccion' in r_aemet.location
    assert 'horas' in r_aemet.location
    assert 'tabla' in r_aemet.location
    assert 'valladolid' in r_aemet.location


@pytest.mark.skip(reason='old')
def test_a_ping(client):
    assert client.get('a').location == url_for('base.aemet', _external=True)


@pytest.mark.skip(reason='old')
def test_favicon_ping(client):
    r_favicon = client.get('favicon.ico')
    assert r_favicon.status_code == 302
    assert '/static/favicon.png' in r_favicon.location


@pytest.mark.skip(reason='old')
def test_static_ping(client):
    assert client.get(url_for('static', filename='peter.pdf', _external=True)).status_code == 404
    assert client.get(url_for('static', filename='favicon.png', _external=True)).status_code == 200


@pytest.mark.skip(reason='old')
def test_new_menus_ping(client):
    r_new_menus = client.get(url_for('menus.new_menus_view', _external=True))
    assert r_new_menus.status_code == 200
