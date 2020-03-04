"""General utils for flask application."""
import logging
import re
from datetime import datetime

from bs4 import BeautifulSoup as Soup
from flask import current_app, request

logger = logging.getLogger(__name__)


class Translator:
    """Translates text from spanish to english and viceversa."""
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
        """Converts months and weekdays from english to spanish.


        Args:
            text (str): text in english.

        Returns:
            str: text in spanish.
        """
        text = text.lower()
        for key, value in cls._e_to_s_months.items():
            text = re.sub(key, value, text, re.I)

        for key, value in cls._e_to_s_weekdays.items():
            text = text.replace(key, value)

        return text

    @classmethod
    def spanish_to_english(cls, text):
        """Converts months and weekdays from spanish to english.

        Args:
            text (str): text in spanish.

        Returns:
            str: text in english.
        """
        text = text.lower()
        for key, value in cls._s_to_e_months.items():
            text = re.sub(key, value, text, re.I)

        for key, value in cls._s_to_e_weekdays.items():
            text = text.replace(key, value)

        return text


def now():
    """Alias for datetime.datetime.now()."""
    return datetime.now()


def get_post_arg(form_name, required=False, strip=False):
    """Gets an arg from a post form and parses it.

    Args:
        form_name (str): key to extract.
        required (bool, optional): Marks the key as required. If it's not
            present, a RunTimeError will be raised. Defaults to False.
        strip (bool, optional): Strip the value before returning. Defaults to False.

    Raises:
        RuntimeError: If `required` is True and the key is not in the form data.

    Returns:
        str: value generated.
    """
    arg = request.form.get(form_name, None)

    if strip and isinstance(arg, str):
        arg = arg.strip()
        if not arg:
            arg = None

    if required and not arg:
        raise RuntimeError("%r is required (%r)" % (form_name, arg))

    return arg


class Tokens:
    """Token manager."""
    @classmethod
    def check_token(cls, web_token):
        """Checks if a token is valid.

        Args:
            web_token (str): token

        Returns:
            bool: wether the token is valid or not.
        """
        for token in cls.gen_tokens():
            if token == web_token:
                return True
        return False

    @classmethod
    def gen_primary_token(cls):
        """Generates a universal valid token."""
        return now().strftime("%Y%m%d%H%M")

    @classmethod
    def gen_tokens(cls):
        """Returns the valid tokens.
        They consist of the generated token and the user-declared ones.
        """
        return [cls.gen_primary_token()] + cls.get_tokens_from_file()

    @classmethod
    def get_tokens_from_file(cls):
        """Gets the token from the token file.

        Returns:
            list of str: tokensself.
        """
        cls.ensure_token_file_exists()
        raw_tokens = current_app.config["TOKEN_FILE_PATH"].read_text().splitlines()
        _tokens = [x for x in raw_tokens if x.strip()]
        tokens = [x.strip() for x in _tokens]

        if len(raw_tokens) != len(tokens):
            cls.update_tokens_file(tokens)
        elif tokens != _tokens:  # Only needs to be called once
            cls.update_tokens_file(tokens)

        return tokens

    @classmethod
    def ensure_token_file_exists(cls):
        """If the token file does not exist, it creates it."""
        if not current_app.config["TOKEN_FILE_PATH"].exists():
            current_app.config["TOKEN_FILE_PATH"].touch()

    @classmethod
    def update_tokens_file(cls, tokens):
        """Updates the token file.

        Args:
            tokens (list of str): tokens to save.
        """
        to_write = "\n".join(tokens)
        current_app.config["TOKEN_FILE_PATH"].write_text(to_write)


class MetaSingleton(type):
    """Metaclass to always make class return the same instance."""

    def __init__(cls, name, bases, attrs):
        super(MetaSingleton, cls).__init__(name, bases, attrs)
        cls._instance = None

    def __call__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(MetaSingleton, cls).__call__(*args, **kwargs)

        # Uncomment line to check possible singleton errors
        # logger.info("Requested Connection (id=%d)", id(cls._instance))
        return cls._instance
