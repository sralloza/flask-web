import pytest
from flask import url_for


@pytest.mark.skip(reason='old')
def test_redirect_menus(client):
    assert client.get('/m').location == url_for('base.menus')


@pytest.mark.skip(reason='old')
def test_redirect_aemet(client):
    assert client.get('/a').location == url_for('base.aemet')


@pytest.mark.skip(reason='old')
def test_redirect_new_menus(client):
    assert client.get('/n').location == url_for('menus.new_menus_view')
    assert client.get('/menus').location == url_for('menus.new_menus_view')


@pytest.mark.skip(reason='old')
def test_redirect_index(client):
    assert client.get('/').location == url_for('menus.new_menus_view')
