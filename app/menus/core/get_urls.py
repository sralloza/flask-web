import logging

import requests
from bs4 import BeautifulSoup as Soup
from requests.exceptions import ConnectionError

logger = logging.getLogger(__name__)
PRINCIPAL_URL = 'https://www.residenciasantiago.es/menus-1/'


def get_menus_urls(principal_url=None, retries=5, index_path=None):
    total_retries = retries
    logger.debug('Getting menus urls')
    if not principal_url:
        principal_url = PRINCIPAL_URL

    while retries:
        try:
            if not index_path:
                response = requests.get(principal_url)
                soup = Soup(response.text, 'html.parser')
            else:
                with open(index_path, 'rb') as fh:
                    soup = Soup(fh.read(), 'html.parser')
            container = soup.findAll('div', {'class': 'j-blog-meta'})
            urls = [x.a['href'] for x in container]
            return urls
        except ConnectionError:
            retries -= 1
            logger.warning('Connection error downloading principal url (%r) (%d retries left)',
                           principal_url, retries)

    logger.critical(
        'Fatal connection error downloading principal url (%r). No urls found (%d retries)',
        principal_url, total_retries)
    return []
