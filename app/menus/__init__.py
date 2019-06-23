from flask import Blueprint

menus = Blueprint('menus', __name__, template_folder='templates')
from . import routes
