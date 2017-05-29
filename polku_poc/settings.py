"""Configuration for the Polku PoC app deployment CLI."""

# pylint: disable=too-few-public-methods

import logging
import os
import shutil
try:
    from ConfigParser import ConfigParser
except ImportError:
    # Python 3.x
    from configparser import ConfigParser


PROJECT_PATH = os.path.abspath(
    os.path.join(os.path.abspath(os.path.dirname(__file__)), '..'))

"""Pathname of user configuration file with configuration overrides."""
CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".polkupoc.ini")

logger = logging.getLogger()
logger.setLevel("INFO")


class Config(object):

    """Polku PoC app deployment CLI configuration."""

    STAGE = "dev"
    ENVIRONMENT_PATH = os.path.join(PROJECT_PATH, "polkupoc.yaml.j2")
    ENVIRONMENT_PARAMS_PATH = os.path.join(PROJECT_PATH, "parameters.yaml")
    ENVIRONMENT_OUTPUTS_PATH = os.path.join(
        PROJECT_PATH, "{environment}-{stage}.outputs.yaml")

    def __init__(self):
            """Load configuration overrides from :data:`CONFIG_FILE`."""
            ini_template = os.path.join(
                PROJECT_PATH, "polku_poc", "polku_poc.ini")
            try:
                if not os.path.isfile(CONFIG_FILE):
                    shutil.copyfile(ini_template, CONFIG_FILE)
                self.from_ini_file("polkupoc")
            except IOError:
                # That's OK, probably running in AWS Lambda
                pass

    def from_ini_file(self, section_name):
        """
        Load configuration overrides from :data:`CONFIG_FILE`.
        :param section_name: Name of the section in the ``*.ini`` file to load.
        """
        parser = ConfigParser()
        parser.read(CONFIG_FILE)
        if parser.has_section(section_name):
            for name, value in parser.items(section_name):
                # Gotcha: The ConfigParser module normalizes keys to lowercase,
                # but we use the convention of uppercase configuration keys
                setattr(self, name.upper(), value)

config = Config()  # pylint: disable=invalid-name
