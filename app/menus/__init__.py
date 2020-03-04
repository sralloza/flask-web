"""Blueprint for menus endpoints."""
from flask import Blueprint

menus_blueprint = Blueprint("menus_blueprint", __name__, template_folder="templates")
from . import routes
