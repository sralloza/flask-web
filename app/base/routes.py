import logging

from flask import redirect, current_app, url_for, request

from . import base
from app.utils import get_last_menus_page

logger = logging.getLogger(__name__)


@base.before_request
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


@base.route('/favicon.ico')
def favicon():
    return redirect(url_for('static', filename='favicon.png'))


@base.route('/')
def index():
    return redirect(url_for('menus.today'))


@base.route('/s')
def redirect_source():
    return redirect('source')


# noinspection PyBroadException
@base.route('/source')
def source():
    if not current_app.config['PARSE_MAIN_WEB']:
        return redirect(current_app.config['LAST_URL'])

    return redirect(get_last_menus_page())


@base.route('/feedback')
def feedback():
    return '<h1>Send feedback to sralloza@gmail.com</h1>'


@base.route('/aemet')
def aemet():
    return redirect(
        'http://www.aemet.es/es/eltiempo/prediccion/municipios/horas/tabla/valladolid-id47186')


@base.route('/a')
def redirect_aemet():
    return redirect('aemet')
