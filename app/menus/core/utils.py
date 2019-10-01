import logging
import re
from typing import List, Union

import requests
from bs4 import BeautifulSoup as Soup
from requests.exceptions import ConnectionError

logger = logging.getLogger(__name__)
PRINCIPAL_URL = 'https://www.residenciasantiago.es/menus-1/'


def get_menus_urls(retries=5):
    """Returns the url to retrieve menus from."""

    # TODO: add option to retrieve all the urls.

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
    """Checks if the string is a date format."""
    x = x.lower()

    return Patterns.day_pattern.search(x) is not None


def filter_data(data: Union[str, List[str]]):
    """Prepares the menus data to be processed.

    Args:
        data: input data.

    Returns:
        Union[str, List[str]]: data processed. It will be the same type as the input.

    """

    if not isinstance(data, (str, list)):
        raise TypeError(f'data must be str or list, not {type(data).__name__}')

    if isinstance(data, str):
        is_string = True
        data = data.splitlines()
    else:
        is_string = False

    while '' in data:
        data.remove('')

    for i in range(len(data)):
        data[i] = data[i].lower().strip()

    for i in range(len(data)):
        if '1 plato:' in data[i]:
            data[i] = data[i].replace('1 plato:', '1er plato:')
        elif '2o plato:' in data[i]:
            data[i] = data[i].replace('2o plato:', '2º plato:')
        elif '2 plato:' in data[i]:
            data[i] = data[i].replace('2 plato:', '2º plato:')
        elif '.' in data[i]:
            data[i] = data[i].replace('.', '')

    out = []
    for i, d in enumerate(data):
        # First check for 'combinado'
        if 'combinado' in d:
            out.append(d.replace('1er plato:', '').strip())
        elif '1er plato:' in d:
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
        elif Patterns.day_pattern.search(d) is not None:
            out.append(Patterns.day_pattern.search(d).group())
        elif Patterns.semi_day_pattern_2.search(d) is not None:
            if Patterns.semi_day_pattern_1.search(data[i - 1]) is not None:
                foo = Patterns.semi_day_pattern_1.search(data[i - 1]).group() + ' de ' + \
                      Patterns.semi_day_pattern_2.search(d).group()
                out.append(foo)
        elif '2º plato' in data[i - 1] and data[i - 1].endswith('con'):
            out[-1] += ' ' + d
        elif '1er plato' in data[i - 1] and i + 1 < len(data) and '2º plato' in data[i + 1]:
            out[-1] += ' ' + d
        else:
            if 'combinado' in data[i - 1] and 'postre' not in d:
                out[-1] += ' ' + d

    if is_string:
        return '\n'.join(out)

    return out


class Patterns:
    """Various patterns used in the core."""

    day_pattern = re.compile(
        r'día\s*:\s*(?P<day>\d+)\s*de\s*(?P<month>\w+)\s*'
        r'de\s*(?P<year>\d{4})\s*\((?P<weekday>\w+)\)',
        re.IGNORECASE)

    semi_day_pattern_1 = re.compile(r'día:\s*(?P<day>\d*)\s*de\s*(?P<month>\w+)$', re.I)
    semi_day_pattern_2 = re.compile(r'(?P<year>\d{4})\s*\(\s*(?P<weekday>\w+)\s*\)', re.I)

    fix_dates_pattern_1 = re.compile(r'(\w+)[\n\s]*(\d{4})', re.I)
    fix_dates_pattern_2 = re.compile(r'(día:)[\s\n]*(\d+)', re.I)