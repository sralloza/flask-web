import requests
from bs4 import BeautifulSoup as Soup
from flask import Flask
from flask import redirect


def create_app(config_filename=None, config_object=None):
    app = Flask(__name__)

    if config_filename:
        app.config.from_pyfile(config_filename)
    elif config_object:
        app.config.from_object(config_object)
    else:
        raise RuntimeError('Select config source (file or object)')

    app.app_context().push()
    return app


app = create_app(config_object='config.Config')


@app.route('/')
def index():
    return redirect('menus')


# noinspection PyBroadException
@app.route('/menus')
def menus():
    if not app.config['PARSE_MAIN_WEB']:
        return redirect(app.config['LAST_URL'])

    principal_url = 'https://www.residenciasantiago.es/menus-1/'

    try:
        response = requests.get(principal_url)
        soup = Soup(response.content, 'html.parser')
        container = soup.findAll('div', {'class': 'j-blog-meta'})

        redirect_url = container[0].a['href']
        return redirect(redirect_url)
    except Exception:
        return redirect(principal_url)


@app.route('/feedback')
def feedback():
    return '<h1>Send feedback to sralloza@gmail.com</h1>'


@app.route('/aemet')
def aemet():
    return redirect(
        'http://www.aemet.es/es/eltiempo/prediccion/municipios/horas/tabla/valladolid-id47186')


if __name__ == '__main__':
    app.run()
