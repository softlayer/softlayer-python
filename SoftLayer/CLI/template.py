"""
    SoftLayer.CLI.template
    ~~~~~~~~~~~~~~~~~~~~~~
    Provides functions for loading/parsing and writing template files. Template
    files are used for storing CLI arguments in the form of a file to be used
    later with the --template option.

    :license: MIT, see LICENSE for more details.
"""
import os.path

from .exceptions import ArgumentError
from SoftLayer.utils import configparser, StringIO


def update_with_template_args(args):
    """ Populates arguments with arguments from the template file, if provided.

    :param dict args: command-line arguments
    """
    if args.get('--template'):
        template_path = args.pop('--template')
        if not os.path.exists(template_path):
            raise ArgumentError(
                'File does not exist [-t | --template] = %s'
                % template_path)

        config = configparser.ConfigParser()
        ini_str = '[settings]\n' + open(
            os.path.expanduser(template_path), 'r').read()
        ini_fp = StringIO(ini_str)
        config.readfp(ini_fp)

        # Merge template options with the options passed in
        for key, value in config.items('settings'):
            option_key = '--%s' % key
            if not args.get(option_key):
                args[option_key] = value


def export_to_template(filename, args, exclude=None):
    """ Exports given options to the given filename in INI format

    :param filename: Filename to save options to
    :param dict args: Arguments to export
    :param list exclude (optional): Exclusion list for options that should not
                                    be exported
    """
    exclude = exclude or []
    exclude.append('--config')
    exclude.append('--really')
    exclude.append('--format')
    exclude.append('--debug')

    with open(filename, "w") as template_file:
        for k, val in args.items():
            if val and k.startswith('-') and k not in exclude:
                k = k.lstrip('-')
                if isinstance(val, list):
                    val = ','.join(val)
                template_file.write('%s=%s\n' % (k, val))
