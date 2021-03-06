from flask import url_for


class TestCss:
    def test_bootstrap(self, client):
        rv = client.get(url_for("static", filename="css/bootstrap.min.css"))
        assert rv.status_code == 200
        assert rv.headers["Content-Type"] == "text/css; charset=utf-8"

    def test_loader(self, client):
        rv = client.get(url_for("static", filename="css/loader.css"))
        assert rv.status_code == 200
        assert rv.headers["Content-Type"] == "text/css; charset=utf-8"

    def test_menus(self, client):
        rv = client.get(url_for("static", filename="css/menus.css"))
        assert rv.status_code == 200
        assert rv.headers["Content-Type"] == "text/css; charset=utf-8"


class TestImages:
    def test_favicon(self, client):
        rv = client.get(url_for("static", filename="images/favicon.png"))
        assert rv.status_code == 200
        assert rv.headers["Content-Type"] == "image/png"


class TestJs:
    def test_beta_datatable_menus(self, client):
        rv = client.get(url_for("static", filename="js/beta-datatable-menus.js"))
        assert rv.status_code == 200
        assert "charset=utf-8" in rv.headers["Content-Type"]

    def test_today_js(self, client):
        rv = client.get(url_for("static", filename="js/today.js"))
        assert rv.status_code == 200
        assert "charset=utf-8" in rv.headers["Content-Type"]
