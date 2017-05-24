"""Setuptools entry point."""

import os
import codecs
from setuptools import setup, find_packages

from polku_poc import __version__, __author__

dirname = os.path.dirname(__file__)
description = "Humilis plug-in to deploy a Lambda microservice"

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except(IOError, ImportError, RuntimeError):
    if os.path.isfile("README.md"):
        long_description = codecs.open(os.path.join(dirname, "README.md"),
                                       encoding="utf-8").read()
    else:
        long_description = description

setup(
    name="humilis-poc",
    include_package_data=True,
    package_data={
        "": ["*.j2", "*.yaml"]},
    packages=find_packages(include=['polku_poc']),
    version=__version__,
    author=__author__,
    author_email="german@findhotel.net",
    url="https://github.com/findhotel/polku-poc",
    license="MIT",
    description=description,
    long_description=long_description,
    install_requires=[
        "sqlalchemy==1.0.0",
        "sqlalchemy-redshift",
        "alembic",
        "humilis-streams",
        "humilis-firehose",
        "humilis-kinesis-proxy",
        "humilis-kinesis-processor",
        "humilis"],
    classifiers=[
        "Programming Language :: Python :: 3"]
)
