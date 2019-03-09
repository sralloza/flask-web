from flask import url_for


def test_redirect_menus(client):
    assert client.get('/m').location == url_for('base.menus')


def test_redirect_aemet(client):
    assert client.get('/a').location == url_for('base.aemet')


def test_redirect_new_menus(client):
    assert client.get('/n').location == url_for('new_menus.new_menus_view')
    assert client.get('/new_menus').location == url_for('new_menus.new_menus_view')


def test_redirect_index(client):
    assert client.get('/').location == url_for('new_menus.new_menus_view')
