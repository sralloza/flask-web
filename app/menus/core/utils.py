import logging
import re
from itertools import count
from typing import List, Union

from bs4 import BeautifulSoup as Soup
from flask import current_app

from app.utils.exceptions import DownloaderError
from app.utils.networking import downloader

logger = logging.getLogger(__name__)

PRINCIPAL_URL = "https://www.residenciasantiago.es/menus-1/"
TEMPLATE = "https://www.residenciasantiago.es/app/blogpage?page=%d&withinCms=&layout=0"


class _Cache:
    redirect_url = None


def get_menus_urls(request_all=False):
    """Returns the url to retrieve menus from."""

    if current_app.config["OFFLINE"]:
        logger.info("Server set to offline, returning emtpy list as menus urls")
        return []

    logger.debug("Getting menus urls")

    url = TEMPLATE % 0  # To avoid possible runtime errors
    urls = []

    for index in count(1):
        try:
            url = TEMPLATE % index
            response = downloader.get(url)
            if "¡Esto es un blog!" in response.text:
                break

            soup = Soup(response.text, "html.parser")
            container = soup.findAll("div", {"class": "j-blog-meta"})
            urls += [x.a["href"] for x in container]

            if not request_all:
                return urls

        except DownloaderError:
            logger.warning("Could not retrieve url %r", url)

            # If there is an error in the first try and only the first one needs to
            # be processed, then return nothing (urls = [])
            if not request_all:
                return urls

    return urls


def get_last_menus_url():
    from app.menus.core.daily_menus_manager import DailyMenusManager

    logger.debug("Getting last menus url")

    if _Cache.redirect_url:
        logger.debug("Found in cache: %s", _Cache.redirect_url)
        return _Cache.redirect_url

    dmm = DailyMenusManager()
    dmm.load_from_database()
    dmm.sort()

    for menu in dmm:
        if menu.url:
            logger.debug("Retrieving url from last menu (%d): %s", menu.id, menu.url)
            _Cache.redirect_url = menu.url
            return menu.url

    logger.warning("No menus with urls saved in database. Using get_menus_urls")
    urls = get_menus_urls()

    if not urls:
        return TEMPLATE % 1

    _Cache.redirect_url = urls[0]
    return _Cache.redirect_url


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
        raise TypeError(f"data must be str or list, not {type(data).__name__}")

    if isinstance(data, str):
        is_string = True
        data = data.splitlines()
    else:
        is_string = False

    while "" in data:
        data.remove("")

    for i in range(len(data)):
        data[i] = data[i].lower().strip()

    for i in range(len(data)):
        if "." in data[i]:
            data[i] = data[i].replace(".", "")

        if re.search(r"1.*\splato:", data[i]):
            data[i] = re.sub(r"1.*\splato:", "1er plato:", data[i])
        elif re.search(r"2.*\splato:", data[i]):
            data[i] = re.sub(r"2.*\splato:", "2º plato:", data[i])

    out = []
    for i, d in enumerate(data):
        # First check for 'combinado'
        if "combinado" in d:
            if "1er plato:" in data[i - 1] and out:
                out[-1] += " " + d.strip()
                continue
            out.append(d.replace("1er plato:", "").strip())
        elif "1er plato:" in d:
            out.append(d)
        elif "2º plato:" in d:
            if "combinado" in data[i - 1]:
                d_prime = d.replace("2º plato:", "").strip()
                if d_prime == d or not d_prime:
                    continue
                out[-1] += " " + d_prime
                continue
            out.append(d)
        elif "comida" in d:
            out.append(d)
        elif "cena" in d:
            out.append(d)
        elif "cóctel" in d or "coctel" in d:  # and d.split() < 3:
            out.append("cóctel")
        elif Patterns.day_pattern.search(d) is not None:
            out.append(Patterns.day_pattern.search(d).group())
        elif Patterns.semi_day_pattern_2.search(d) is not None:
            if Patterns.semi_day_pattern_1.search(data[i - 1]) is not None:
                foo = (
                    Patterns.semi_day_pattern_1.search(data[i - 1]).group()
                    + " de "
                    + Patterns.semi_day_pattern_2.search(d).group()
                )
                out.append(foo)
        elif (
            "2º plato" in data[i - 1]
            and data[i - 1].endswith("con")
            and "postre" not in d
        ):
            out[-1] += " " + d
        elif (
            "1er plato" in data[i - 1]
            and i + 1 < len(data)
            and "2º plato" in data[i + 1]
            and "postre" not in d
        ):
            out[-1] += " " + d
        else:
            if "combinado" in data[i - 1] and "postre" not in d:
                out[-1] += " " + d

    if is_string:
        return "\n".join(out)

    return out


class Patterns:
    """Various patterns used in the core."""

    day_pattern = re.compile(
        r"día\s*:\s*(?P<day>\d+)\s*de\s*(?P<month>\w+)\s*"
        r"de\s*(?P<year>\d{4})\s*\((?P<weekday>\w+)\)",
        re.IGNORECASE,
    )

    semi_day_pattern_1 = re.compile(r"día:\s*(?P<day>\d*)\s*de\s*(?P<month>\w+)$", re.I)
    semi_day_pattern_2 = re.compile(
        r"(?P<year>\d{4})\s*\(\s*(?P<weekday>\w+)\s*\)", re.I
    )

    fix_dates_pattern_1 = re.compile(r"(\w+)[\n\s]*(\d{4})", re.I)
    fix_dates_pattern_2 = re.compile(r"(día:)[\s\n]*(\d+)", re.I)
    fix_dates_pattern_3 = re.compile(
        r"(día\s*:\s*\d+\s*de\s*\w+\s*de\s*\d{4}\s*\(\w+(?![\)a-zA-ZáéíóúÁÉÍÓÚ]))",
        re.IGNORECASE,
    )

    fix_content_pattern_1 = re.compile(
        # r"(?<!:)([\w\sÁÉÍÓÚÑ]+)\n([\w\sÁÉÍÓÚÑ]+)(?!\w*:)", re.IGNORECASE
        r"(?<!:)([A-Z\sÁÉÍÓÚÑ]+)\n([A-Z\sÁÉÍÓÚÑ]{3,})(?!([\wº]*[:\d]))",
        re.IGNORECASE,
    )
    fix_content_pattern_2 = re.compile(r"(\s){2,}", re.IGNORECASE)
    fix_content_pattern_3 = re.compile(r"(\w+)(?:[ \t]+)(postre:)", re.IGNORECASE)
