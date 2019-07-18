import logging

import requests
from bs4 import BeautifulSoup as Soup
from requests.exceptions import ConnectionError

logger = logging.getLogger(__name__)

PRINCIPAL_URL = 'https://www.residenciasantiago.es/menus-1/'


class _Static:
    redirect_url = None


def get_last_menus_page(retries=5):
    if _Static.redirect_url:
        return _Static.redirect_url

    total_retries = retries
    logger.debug('Getting last menus url')

    while retries:
        try:
            response = requests.get(PRINCIPAL_URL)
            soup = Soup(response.text, 'html.parser')
            container = soup.findAll('div', {'class': 'j-blog-meta'})
            urls = [x.a['href'] for x in container]
            return urls[0]
        except ConnectionError:
            retries -= 1
            logger.warning('Connection error downloading principal url (%r) (%d retries left)',
                           PRINCIPAL_URL, retries)

    logger.critical(
        'Fatal connection error downloading principal url (%r) (%d retries)',
        PRINCIPAL_URL, total_retries)
    return PRINCIPAL_URL
