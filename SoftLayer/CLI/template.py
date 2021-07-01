"""
    SoftLayer.CLI.template
    ~~~~~~~~~~~~~~~~~~~~~~
    Provides functions for loading/parsing and writing template files. Template
    files are used for storing CLI arguments in the form of a file to be used
    later with the --template option.

    :license: MIT, see LICENSE for more details.
"""

# pylint: disable=redefined-argument-from-local
import configparser
import io
import os.path


class TemplateCallback(object):
    """Callback to use to populate click arguments with a template."""

    def __init__(self, list_args=None):
        self.list_args = list_args or []

    def __call__(self, ctx, param, value):
        if value is None:
            return

        with open(os.path.expanduser(value), 'r') as file_handle:
            config = configparser.ConfigParser()
            ini_str = '[settings]\n' + file_handle.read()
            ini_fp = io.StringIO(ini_str)
            config.read_file(ini_fp)

        # Merge template options with the options passed in
        args = {}
        for key, value in config.items('settings'):
            if key in self.list_args:
                value = value.split(',')

            if not args.get(key):
                args[key] = value

        if ctx.default_map is None:
            ctx.default_map = {}
        ctx.default_map.update(args)


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
