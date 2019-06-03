from flask import Blueprint

blue = Blueprint('base', __name__, template_folder='templates')
from . import routes
