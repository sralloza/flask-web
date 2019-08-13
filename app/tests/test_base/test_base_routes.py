from unittest import mock


def test_user_agent_filter(client):
    assert client.get('/', headers={'User-Agent': 'python-requests/2.21.0'}).status_code == 401
    assert client.get('/', headers={'User-Agent': '-'}).status_code == 401
    assert client.get('/', headers={'User-Agent': 'Rift/2.0'}).status_code == 401


def test_redirect_favicon(client):
    rv = client.get('/favicon.ico')
    assert rv.status_code == 301
    assert rv.location == 'http://menus.sralloza.es/static/images/favicon.png'


def test_index(client):
    rv = client.get('/')
    assert 200 <= rv.status_code <= 399


def test_redirect_index(client):
    rv = client.get('/')
    assert rv.status_code == 302
    assert rv.location == 'http://menus.sralloza.es/hoy'


def test_redirect_source(client):
    rv = client.get('/s')
    assert rv.status_code == 301
    assert rv.location == 'http://menus.sralloza.es/source'


@mock.patch('app.base.routes.get_last_menus_page', return_value='http://example.com')
def test_source(get_last_menus_page_mock, client):
    rv = client.get('/source')
    assert rv.status_code == 302
    assert rv.location == 'http://example.com'

    get_last_menus_page_mock.assert_called_once_with()


def test_feedback(client):
    rv = client.get('/feedback')
    assert rv.status_code == 200
    assert b'<h1>Send feedback to sralloza@gmail.com</h1>' in rv.data


def test_redirect_aemet(client):
    rv = client.get('/a')
    assert rv.status_code == 301
    assert rv.location == 'http://menus.sralloza.es/aemet'


def test_aemet(client):
    aemet = 'http://www.aemet.es/es/eltiempo/prediccion/municipios/horas/tabla/valladolid-id47186'
    rv = client.get('/aemet')
    assert rv.status_code == 301
    assert rv.location == aemet
