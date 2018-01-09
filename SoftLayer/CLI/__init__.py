"""
    SoftLayer.CLI
    ~~~~~~~~~~~~~~
    Contains all code related to the CLI interface

    :license: MIT, see LICENSE for more details.
"""
# pylint: disable=w0401, invalid-name
import logging

from SoftLayer.CLI.helpers import *  # NOQA

logger = logging.getLogger()
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)
