from pathlib import Path

from setuptools import find_packages, setup


def get_version():
    path = Path(__file__).with_name("app").joinpath("VERSION")
    return path.read_text().strip()


def get_requirements():
    path = Path(__file__).with_name("requirements.txt")
    return [x.strip() for x in path.read_text().split("\n") if x.strip()]


setup(
    version=get_version(),
    name="app",
    pagackes=find_packages(),
    requirements=get_requirements(),
    # package_data={"": [""]},
)
