from flask import Blueprint

new_menus = Blueprint('new_menus', __name__, template_folder='templates')
from . import routes
