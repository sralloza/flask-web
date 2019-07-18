import logging

import requests
from bs4 import BeautifulSoup as Soup
from requests.exceptions import ConnectionError

logger = logging.getLogger(__name__)
PRINCIPAL_URL = 'https://www.residenciasantiago.es/menus-1/'


def get_menus_urls(retries=5):
    total_retries = retries
    logger.debug('Getting menus urls')

    while retries:
        try:
            response = requests.get(PRINCIPAL_URL)
            soup = Soup(response.text, 'html.parser')
            container = soup.findAll('div', {'class': 'j-blog-meta'})
            urls = [x.a['href'] for x in container]
            return urls
        except ConnectionError:
            retries -= 1
            logger.warning('Connection error downloading principal url (%r) (%d retries left)',
                           PRINCIPAL_URL, retries)

    logger.critical(
        'Fatal connection error downloading principal url (%r) (%d retries)',
        PRINCIPAL_URL, total_retries)
    return []
