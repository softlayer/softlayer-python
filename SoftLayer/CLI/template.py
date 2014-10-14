"""
    SoftLayer.CLI.template
    ~~~~~~~~~~~~~~~~~~~~~~
    Provides functions for loading/parsing and writing template files. Template
    files are used for storing CLI arguments in the form of a file to be used
    later with the --template option.

    :license: MIT, see LICENSE for more details.
"""
import os.path

from SoftLayer import utils


def update_with_template_args(args, list_args=None):
    """Populates arguments with arguments from the template file, if provided.

    :param dict args: command-line arguments
    """
    if not args.get('template'):
        return

    list_args = list_args or []

    template_path = args.pop('template')

    config = utils.configparser.ConfigParser()
    ini_str = '[settings]\n' + open(
        os.path.expanduser(template_path), 'r').read()
    ini_fp = utils.StringIO(ini_str)
    config.readfp(ini_fp)

    # Merge template options with the options passed in
    for key, value in config.items('settings'):
        if key in list_args:
            value = value.split(',')
        if not args.get(key):
            args[key] = value


def export_to_template(filename, args, exclude=None):
    """Exports given options to the given filename in INI format.

    :param filename: Filename to save options to
    :param dict args: Arguments to export
    :param list exclude (optional): Exclusion list for options that should not
                                    be exported
    """
    exclude = exclude or []
    exclude.append('config')
    exclude.append('really')
    exclude.append('format')
    exclude.append('debug')

    with open(filename, "w") as template_file:
        for k, val in args.items():
            if val and k not in exclude:
                if isinstance(val, tuple):
                    val = ','.join(val)
                if isinstance(val, list):
                    val = ','.join(val)
                template_file.write('%s=%s\n' % (k, val))
