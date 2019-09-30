import logging
import re
from datetime import datetime

import requests
from bs4 import BeautifulSoup as Soup
from flask import request
from requests.exceptions import ConnectionError

logger = logging.getLogger(__name__)

PRINCIPAL_URL = "https://www.residenciasantiago.es/menus-1/"


class _Cache:
    redirect_url = None


class Translator:
    _e_to_s_weekdays = {
        "monday": "lunes",
        "tuesday": "martes",
        "wednesday": "miércoles",
        "thursday": "jueves",
        "friday": "viernes",
        "saturday": "sábado",
        "sunday": "domingo",
    }
    _s_to_e_weekdays = {
        "lunes": "monday",
        "martes": "tuesday",
        "miércoles": "wednesday",
        "jueves": "thursday",
        "viernes": "friday",
        "sábado": "saturday",
        "domingo": "sunday",
    }

    _e_to_s_months = {
        "january": "enero",
        "february": "febrero",
        "march": "marzo",
        "april": "abril",
        "may": "mayo",
        "june": "junio",
        "july": "julio",
        "august": "agosto",
        "september": "septiembre",
        "october": "octubre",
        "november": "noviembre",
        "december": "diciembre",
    }
    _s_to_e_months = {
        "enero": "january",
        "febrero": "february",
        "marzo": "march",
        "abril": "april",
        "mayo": "may",
        "junio": "june",
        "julio": "july",
        "agosto": "august",
        "septiembre": "september",
        "octubre": "october",
        "noviembre": "november",
        "diciembre": "december",
    }

    @classmethod
    def english_to_spanish(cls, text):
        """Converts months and weekdays from english to spanish."""
        text = text.lower()
        for key, value in cls._e_to_s_months.items():
            text = re.sub(key, value, text, re.I)

        for key, value in cls._e_to_s_weekdays.items():
            text = text.replace(key, value)

        return text

    @classmethod
    def spanish_to_english(cls, text):
        """Converts months and weekdays from spanish to english."""
        text = text.lower()
        for key, value in cls._s_to_e_months.items():
            text = re.sub(key, value, text, re.I)

        for key, value in cls._s_to_e_weekdays.items():
            text = text.replace(key, value)

        return text


def get_last_menus_page(retries=5):
    if _Cache.redirect_url:
        return _Cache.redirect_url

    total_retries = retries
    logger.debug("Getting last menus url")

    while retries:
        try:
            response = requests.get(PRINCIPAL_URL)
            soup = Soup(response.text, "html.parser")
            container = soup.findAll("div", {"class": "j-blog-meta"})
            urls = [x.a["href"] for x in container]
            url = urls[0]
            _Cache.redirect_url = url
            return url
        except ConnectionError:
            retries -= 1
            logger.warning(
                "Connection error downloading principal url (%r) (%d retries left)",
                PRINCIPAL_URL,
                retries,
            )

    logger.critical(
        "Fatal connection error downloading principal url (%r) (%d retries)",
        PRINCIPAL_URL,
        total_retries,
    )
    return PRINCIPAL_URL


def now():
    return datetime.now()


def get_post_arg(form_name, required=False, strip=False):
    arg = request.form.get(form_name, None)

    if strip and isinstance(arg, str):
        arg = arg.strip()
        if not arg:
            arg = None

    if required and not arg:
        raise RuntimeError("%r is required (%r)" % (form_name, arg))

    return arg


def gen_token():
    return now().strftime("%Y%m%d%H%M")
