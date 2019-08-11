import logging

import requests
from bs4 import BeautifulSoup as Soup
from requests.exceptions import ConnectionError

from app.menus.core import Patterns

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


def has_day(x):
    x = x.lower()

    return Patterns.day_pattern.search(x) is not None


def filter_data(data):
    while '' in data:
        data.remove('')

    for i in range(len(data)):
        data[i] = data[i].lower().strip()

    out = []
    for i, d in enumerate(data):
        if '1er plato:' in d:
            out.append(d)
        elif '2º plato:' in d:
            if 'combinado' in data[i - 1]:
                d = d.replace('2º plato:', '').strip()
                out[-1] += ' ' + d
                continue
            out.append(d)
        elif 'comida' in d:
            out.append(d)
        elif 'cena' in d:
            out.append(d)
        elif 'cóctel' in d or 'coctel' in d:
            out.append('cóctel')
        elif 'combinado' in d:
            out.append(d.replace('1er plato:', '').strip())
        elif Patterns.day_pattern.search(d) is not None:
            out.append(Patterns.day_pattern.search(d).group())
        elif Patterns.semi_day_pattern_2.search(d) is not None:
            if Patterns.semi_day_pattern_1.search(data[i - 1]) is not None:
                foo = Patterns.semi_day_pattern_1.search(data[i - 1]).group() + ' de ' + \
                      Patterns.semi_day_pattern_2.search(d).group()
                out.append(foo)
        else:
            if 'combinado' in data[i - 1] and 'postre' not in d:
                out[-1] += ' ' + d
    return out
