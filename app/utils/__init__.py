import logging
import re
from datetime import datetime

import requests
from bs4 import BeautifulSoup as Soup
from flask import current_app, request
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


class Tokens:
    @classmethod
    def check_token(cls, web_token):
        for token in cls.gen_tokens():
            if token == web_token:
                return True
        return False

    @classmethod
    def gen_primary_token(cls):
        return now().strftime("%Y%m%d%H%M")

    @classmethod
    def gen_tokens(cls):
        return [cls.gen_primary_token()] + cls.get_tokens_from_file()

    @classmethod
    def get_tokens_from_file(cls):
        cls.ensure_token_file_exists()
        raw_tokens = current_app.config["TOKEN_FILE_PATH"].read_text().splitlines()
        tokens = [x for x in raw_tokens if x]

        if len(raw_tokens) != len(tokens):
            cls.update_tokens(tokens)

        return tokens

    @classmethod
    def ensure_token_file_exists(cls):
        if not current_app.config["TOKEN_FILE_PATH"].exists():
            current_app.config["TOKEN_FILE_PATH"].touch()

    @classmethod
    def update_tokens(cls, tokens):
        to_write = "\n".join(tokens)
        current_app.config["TOKEN_FILE_PATH"].write_text(to_write)
