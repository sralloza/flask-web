from flask import Blueprint

new_menus = Blueprint('new_menus', __name__)
from . import routes
