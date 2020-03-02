"""Utils for menus' core."""
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
    """Static class to store the redirect_url in case
    it is needed again."""

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
    """Returns the most recent menus url, using the cache, the DMM and
    finally, the main web.

    Returns:
        str: most recent menus url.
    """
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


def has_day(anything):
    """Checks if the string is a date format."""
    anything = anything.lower()

    return Patterns.day_pattern.search(anything) is not None


def filter_data(data: Union[str, List[str]]):
    """Prepares the menus data to be processed.

    Args:
        data: input data.

    Returns:
        str or list of str: data processed. It will be the same type as the input.

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

    for index, line in enumerate(data):
        data[index] = data[index].lower().strip()

    for index, line in enumerate(data):
        if "." in data[index]:
            data[index] = data[index].replace(".", "")

        if re.search(r"1.*\splato:", data[index]):
            data[index] = re.sub(r"1.*\splato:", "1er plato:", data[index])
        elif re.search(r"2.*\splato:", data[index]):
            data[index] = re.sub(r"2.*\splato:", "2º plato:", data[index])

    out = []
    for index, line in enumerate(data):
        # First check for 'combinado'
        if len(line) <= 2:
            continue
        if "combinado" in line:
            if "1er plato:" in data[index - 1] and out:
                out[-1] += " " + line.strip()
                continue
            out.append(line.replace("1er plato:", "").strip())
        elif "1er plato:" in line:
            out.append(line)
        elif "2º plato:" in line:
            if "combinado" in data[index - 1]:
                d_prime = line.replace("2º plato:", "").strip()
                if d_prime == line or not d_prime:
                    continue
                out[-1] += " " + d_prime
                continue
            out.append(line)
        elif Patterns.pattern_lunch.search(line):
            out.append(line)
        elif Patterns.pattern_dinner.search(line):
            out.append(line)
        elif "cóctel" in line or "coctel" in line:  # and d.split() < 3:
            out.append("cóctel")
        elif Patterns.day_pattern.search(line) is not None:
            out.append(Patterns.day_pattern.search(line).group())
        elif Patterns.semi_day_pattern_2.search(line) is not None:
            if Patterns.semi_day_pattern_1.search(data[index - 1]) is not None:
                good_to_go = (
                    Patterns.semi_day_pattern_1.search(data[index - 1]).group()
                    + " de "
                    + Patterns.semi_day_pattern_2.search(line).group()
                )
                out.append(good_to_go)
        # I don't know how, but this shit works. Don't ask
        elif (
            "2º plato" in data[index - 1]
            and data[index - 1].endswith("con")
            and "postre" not in line
        ):
            out[-1] += " " + line

        # I don't know how, but this shit works. Don't ask
        elif (
            "1er plato" in data[index - 1]
            and index + 1 < len(data)
            and "2º plato" in data[index + 1]
            and "postre" not in line
        ):
            out[-1] += " " + line
        else:
            if "combinado" in data[index - 1] and "postre" not in line:
                out[-1] += " " + line
            elif "comida" in data[index - 1] or "cena" in data[index - 1]:
                out.append("1er plato: " + line)

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
        r"d[íÍ]a\s*:\s*(\d+)\s*de\s*(\w+)\s*de\s*(\d{4})\s*\(?\s*([\wá-úÁ-Ú]+)\s*\)?",
        re.IGNORECASE,
    )

    fix_content_pattern_1 = re.compile(
        # r"(?<!:)([\w\sÁÉÍÓÚÑ]+)\n([\w\sÁÉÍÓÚÑ]+)(?!\w*:)", re.IGNORECASE
        r"(?<!:)([A-Z\sÁÉÍÓÚÑ]+)\n([A-Z\sÁÉÍÓÚÑ]{3,})(?!([\wº]*[;:\d]))",
        re.IGNORECASE,
    )
    fix_content_pattern_2 = re.compile(r"([ \t]){2,}", re.IGNORECASE)
    fix_content_pattern_3 = re.compile(r"(\w+)(?:[ \t]+)(postre:)", re.IGNORECASE)

    pattern_lunch = re.compile(r"comida[:;]", re.IGNORECASE)
    pattern_dinner = re.compile(r"cena(r)?[:;]", re.IGNORECASE)
