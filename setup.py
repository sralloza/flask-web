"""Installer designed to install a development version of the
application during testing:
$ python -m pip install -e .
"""
from pathlib import Path

from setuptools import find_packages, setup


def get_version():
    """Returns the version of the application.

    Returns:
        str: version of the application.
    """
    path = Path(__file__).with_name("app").joinpath("VERSION")
    return path.read_text().strip()


def get_requirements():
    """Returns the requirements of the application

    Returns:
        list of str: requirements of the application.
    """
    path = Path(__file__).with_name("requirements.txt")
    return [x.strip() for x in path.read_text().split("\n") if x.strip()]


setup(
    version=get_version(),
    name="app",
    pagackes=find_packages(),
    requirements=get_requirements(),
)
