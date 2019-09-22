from flask import Blueprint


def test_import_blueprint():
    from app.base import base_blueprint
    assert isinstance(base_blueprint, Blueprint)