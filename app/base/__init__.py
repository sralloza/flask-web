"""Blueprint for base endpoints."""
from flask import Blueprint

base_blueprint = Blueprint("base_blueprint", __name__, template_folder="templates")
from . import routes
