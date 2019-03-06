from flask import Blueprint

blue = Blueprint('base', __name__)
from . import routes
