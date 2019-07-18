import logging

import requests
from bs4 import BeautifulSoup as Soup

logger = logging.getLogger(__name__)


class _Static:
    redirect_url = None


def get_last_menus_page():
    principal_url = 'https://www.residenciasantiago.es/menus-1/'

    if _Static.redirect_url:
        return _Static.redirect_url

    try:
        response = requests.get(principal_url)
        soup = Soup(response.text, 'html.parser')
        container = soup.findAll('div', {'class': 'j-blog-meta'})

        redirect_url = container[0].a['href']
        _Static.redirect_url = redirect_url
        return redirect_url
    except Exception:
        logger.exception('Failed detecting this week\'s menus url')
        return principal_url
