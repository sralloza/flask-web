import logging

import requests
from bs4 import BeautifulSoup as Soup
from requests.exceptions import ConnectionError

logger = logging.getLogger(__name__)


def get_menus_urls(principal_url=None, retries=5, index_path=None):
    logger.debug('Getting menus urls')
    if not principal_url:
        principal_url = 'https://www.residenciasantiago.es/menus-1/'

    while retries:
        try:
            if not index_path:
                response = requests.get(principal_url)
                soup = Soup(response.content, 'html.parser')
            else:
                with open(index_path, 'rb') as fh:
                    soup = Soup(fh.read(), 'html.parser')
            container = soup.findAll('div', {'class': 'j-blog-meta'})
            urls = [x.a['href'] for x in container]
            return urls
        except ConnectionError:
            logger.warning('Connection error downloading principal url (%r)', principal_url)
            retries -= 1

    logger.critical(
        'Fatal connection error downloading principal url (%r). No urls found (%d retries)',
        principal_url, retries)
    return []
