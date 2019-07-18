import pytest


def test_user_agent_filter(client):
    assert client.get('/', headers={'User-Agent': 'python-requests/2.21.0'}).status_code == 401
    assert client.get('/', headers={'User-Agent': '-'}).status_code == 401
    assert client.get('/', headers={'User-Agent': 'Rift/2.0'}).status_code == 401


def test_redirect_favicon(client):
    rv = client.get('/favicon.ico')
    assert rv.status_code == 301
    assert rv.location == 'https://menus.sralloza.es/static/images/favicon.png'


def test_favicon(client):
    rv = client.get('/static/images/favicon.png')
    assert rv.status_code == 200
    assert rv.headers['Content-Type'] == 'image/png'


def test_index(client):
    rv = client.get('/')
    assert 200 <= rv.status_code <= 399


def test_redirect_index(client):
    rv = client.get('/')
    assert rv.status_code == 301
    assert rv.location == 'https://menus.sralloza.es/hoy'


def test_redirect_source(client):
    rv = client.get('/s')
    assert rv.status_code == 301
    assert rv.location == 'https://menus.sralloza.es/source'


@pytest.mark.skip
def test_source():
    pass


def test_feedback(client):
    rv = client.get('/feedback')
    assert rv.status_code == 200
    assert b'<h1>Send feedback to sralloza@gmail.com</h1>' in rv.data


def test_redirect_aemet(client):
    rv = client.get('/a')
    assert rv.status_code == 301
    assert rv.location == 'https://menus.sralloza.es/aemet'


def test_aemet(client):
    aemet = 'http://www.aemet.es/es/eltiempo/prediccion/municipios/horas/tabla/valladolid-id47186'
    rv = client.get('/aemet')
    assert rv.status_code == 301
    assert rv.location == aemet
