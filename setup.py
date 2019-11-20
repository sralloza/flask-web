from pathlib import Path

from setuptools import find_packages, setup


def get_version():
    path = Path(__file__).with_name("VERSION")
    return path.read_text().strip()


setup(version=get_version(), name="app", pagackes=find_packages())
