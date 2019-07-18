import logging

from flask import redirect, current_app, url_for, request

from app.utils import get_last_menus_page
from . import base_blueprint

logger = logging.getLogger(__name__)


@base_blueprint.before_request
def before_request():
    if request.headers.get('User-Agent') is None:
        return 'A user agent must be provided', 401

    user_agent = request.headers.get('User-Agent').lower()
    if 'rift' in user_agent:
        logger.debug('Detected Rift as user agent (%r)', request.headers.get('User-Agent'))
        return 'Rift not allowed', 401
    if 'python' in user_agent:
        logger.debug('Detected Python as user agent (%r)', request.headers.get('User-Agent'))
        return 'Python requests not allowed', 401
    if user_agent == '-':
        logger.debug('Not user agent provided (%r)', request.headers.get('User-Agent'))
        return 'A user agent must be provided', 401


@base_blueprint.route('/favicon.ico')
def favicon():
    return redirect(url_for('static', filename='images/favicon.png', _scheme='https', _external=True),
                    code=301)


@base_blueprint.route('/')
def index():
    return redirect(url_for('menus_blueprint.today', _scheme='https', _external=True), code=301)


@base_blueprint.route('/s')
def redirect_source():
    return redirect(url_for('base_blueprint.source', _scheme='https', _external=True), code=301)


# noinspection PyBroadException
@base_blueprint.route('/source')
def source():
    if not current_app.config['PARSE_MAIN_WEB']:
        return redirect(current_app.config['LAST_URL'])

    return redirect(get_last_menus_page())


@base_blueprint.route('/feedback')
def feedback():
    return '<h1>Send feedback to sralloza@gmail.com</h1>'


@base_blueprint.route('/a')
def redirect_aemet():
    return redirect(url_for('base_blueprint.aemet', _scheme='https', _external=True), code=301)


@base_blueprint.route('/aemet')
def aemet():
    return redirect(
        'http://www.aemet.es/es/eltiempo/prediccion/municipios/horas/tabla/valladolid-id47186',
        code=301)
