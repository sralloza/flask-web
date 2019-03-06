import requests
from bs4 import BeautifulSoup as Soup
from flask import redirect, current_app

from . import blue


@blue.route('/')
def index():
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
        return redirect(principal_url)


@blue.route('/feedback')
def feedback():
    return '<h1>Send feedback to sralloza@gmail.com</h1>'


@blue.route('/aemet')
def aemet():
    return redirect(
        'http://www.aemet.es/es/eltiempo/prediccion/municipios/horas/tabla/valladolid-id47186')
