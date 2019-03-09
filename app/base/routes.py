import logging

import requests
from bs4 import BeautifulSoup as Soup
from flask import redirect, current_app, url_for, request

from . import blue

logger = logging.getLogger(__name__)


@blue.before_request
def before_request():
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


@blue.route('/favicon.ico')
def favicon():
    return redirect(url_for('static', filename='favicon.png'))


@blue.route('/')
def index():
    return redirect('menus')


@blue.route('/m')
def redirect_menus():
    return redirect('menus')


# noinspection PyBroadException
@blue.route('/menus')
def menus():
    if not current_app.config['PARSE_MAIN_WEB']:
        return redirect(current_app.config['LAST_URL'])

    principal_url = 'https://www.residenciasantiago.es/menus-1/'

    try:
        response = requests.get(principal_url)
        soup = Soup(response.content, 'html.parser')
        container = soup.findAll('div', {'class': 'j-blog-meta'})

        redirect_url = container[0].a['href']
        return redirect(redirect_url)
    except Exception:
        logger.exception('Failed detecting this week\'s menus url')
        return redirect(principal_url)


@blue.route('/feedback')
def feedback():
    return '<h1>Send feedback to sralloza@gmail.com</h1>'


@blue.route('/aemet')
def aemet():
    return redirect(
        'http://www.aemet.es/es/eltiempo/prediccion/municipios/horas/tabla/valladolid-id47186')


@blue.route('/a')
def redirect_aemet():
    return redirect('aemet')
