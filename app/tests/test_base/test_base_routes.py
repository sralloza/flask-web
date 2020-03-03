from unittest import mock

import pytest
from flask.testing import FlaskClient
from werkzeug.wrappers import BaseResponse


def test_user_agent_filter(app):
    client = FlaskClient(app, BaseResponse)
    del client.environ_base["HTTP_USER_AGENT"]

    assert client.get("/").status_code == 401
    assert (
        client.get("/", headers={"User-Agent": "python-requests/2.21.0"}).status_code
        == 401
    )
    assert client.get("/", headers={"User-Agent": "-"}).status_code == 401
    assert client.get("/", headers={"User-Agent": "Rift/2.0"}).status_code == 401
    assert client.get("/", headers={"User-Agent": "YandexBot/3.0"}).status_code == 401
    assert client.get("/", headers={"User-Agent": "SMTBot/1.0"}).status_code == 401
    assert (
        client.get("/", headers={"User-Agent": "Nimbostratus-Bot/v1.3.2"}).status_code
        == 401
    )
    assert client.get("/", headers={"User-Agent": "My-Custom-Bot"}).status_code == 401


def test_redirect_favicon(client):
    rv = client.get("/favicon.ico")
    assert rv.status_code == 301
    assert rv.location == "http://menus.sralloza.es/static/images/favicon.png"


def test_index(client):
    rv = client.get("/")
    assert 200 <= rv.status_code <= 399


def test_version_redirect(client):
    rv = client.get("/v")
    assert rv.status_code == 301
    assert rv.location == "http://menus.sralloza.es/version"


def test_version(client):
    from app import get_version

    rv = client.get("/version")
    assert rv.status_code == 200
    assert get_version().encode() in rv.data


def test_redirect_index(client):
    rv = client.get("/")
    assert rv.status_code == 302
    assert rv.location == "http://menus.sralloza.es/hoy"


def test_redirect_source(client):
    rv = client.get("/s")
    assert rv.status_code == 301
    assert rv.location == "http://menus.sralloza.es/source"


@mock.patch(
    "app.base.routes.get_last_menus_url",
    return_value="http://example.com",
    autospec=True,
)
def test_source(get_last_menus_url_mock, client):
    rv = client.get("/source")
    assert rv.status_code == 302
    assert rv.location == "http://example.com"

    get_last_menus_url_mock.assert_called_once_with()


def test_feedback(client):
    rv = client.get("/feedback")
    assert rv.status_code == 200
    assert b"<h1>Send feedback to sralloza@gmail.com</h1>" in rv.data


def test_redirect_aemet(client):
    rv = client.get("/a")
    assert rv.status_code == 301
    assert rv.location == "http://menus.sralloza.es/aemet"


def test_aemet(client):
    aemet = "http://www.aemet.es/es/eltiempo/prediccion/municipios/horas/tabla/valladolid-id47186"
    rv = client.get("/aemet")
    assert rv.status_code == 301
    assert rv.location == aemet


_urls_notifications_test = ["notificaciones", "notifications", "alerts", "alertas"]


@pytest.mark.parametrize("url", _urls_notifications_test)
def test_notifications(client, url):
    rv = client.get("/" + url)
    assert rv.status_code == 200

    assert b"primary" in rv.data
    assert b"secondary" in rv.data
    assert b"success" in rv.data
    assert b"danger" in rv.data
    assert b"warning" in rv.data
    assert b"info" in rv.data


_footer_urls_test = ["add", "del", "feedback", "version"] + _urls_notifications_test


@pytest.mark.parametrize("url", _footer_urls_test)
def test_footer(client, url):
    rv = client.get("/" + url)
    assert b"https://sralloza.es" in rv.data
    assert "¿Algún error? ¿Alguna sugerencia?".encode("utf-8") in rv.data
    assert "© 2018-2020 Diego Alloza González".encode("utf-8") in rv.data
