from flask import url_for


class TestStaticFiles:
    class TestCss:
        def test_menus(self, client):
            rv = client.get(url_for('static', filename='css/menus.css'))
            assert rv.status_code == 200
            assert rv.headers['Content-Type'] == 'text/css; charset=utf-8'

    class TestImages:
        def test_favicon(self, client):
            rv = client.get(url_for('static', filename='images/favicon.png'))
            assert rv.status_code == 200
            assert rv.headers['Content-Type'] == 'image/png'

    class TestJs:
        def test_beta_datatable_menus(self, client):
            rv = client.get(url_for('static', filename='js/beta-datatable-menus.js'))
            assert rv.status_code == 200
            assert rv.headers['Content-Type'] == 'text/plain; charset=utf-8'

        def test_today_js(self, client):
            rv = client.get(url_for('static', filename='js/today-js.js'))
            assert rv.status_code == 200
            assert rv.headers['Content-Type'] == 'text/plain; charset=utf-8'
