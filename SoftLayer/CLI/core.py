"""
    SoftLayer.CLI.core
    ~~~~~~~~~~~~~~~~~~
    Core for the SoftLayer CLI

    :license: MIT, see LICENSE for more details.
"""
from __future__ import print_function
import logging
import os
import sys
import time
import types

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting
from SoftLayer import consts

# pylint: disable=too-many-public-methods, broad-except, unused-argument
# pylint: disable=redefined-builtin, super-init-not-called, arguments-differ

START_TIME = time.time()
DEBUG_LOGGING_MAP = {
    0: logging.CRITICAL,
    1: logging.WARNING,
    2: logging.INFO,
    3: logging.DEBUG
}

VALID_FORMATS = ['table', 'raw', 'json', 'jsonraw']
DEFAULT_FORMAT = 'raw'
if sys.stdout.isatty():
    DEFAULT_FORMAT = 'table'


class CommandLoader(click.MultiCommand):
    """Loads module for click."""

    def __init__(self, *path, **attrs):
        click.MultiCommand.__init__(self, **attrs)
        self.path = path

    def list_commands(self, ctx):
        """List all sub-commands."""
        env = ctx.ensure_object(environment.Environment)
        env.load()

        return sorted(env.list_commands(*self.path))

    def get_command(self, ctx, name):
        """Get command for click."""
        env = ctx.ensure_object(environment.Environment)
        env.load()

        # Do alias lookup (only available for root commands)
        if len(self.path) == 0:
            name = env.resolve_alias(name)

        new_path = list(self.path)
        new_path.append(name)
        module = env.get_command(*new_path)
        if isinstance(module, types.ModuleType):
            return CommandLoader(*new_path, help=module.__doc__ or '')
        else:
            return module


@click.group(help="SoftLayer Command-line Client",
             epilog="""To use most commands your SoftLayer
username and api_key need to be configured. The easiest way to do that is to
use: 'slcli setup'""",
             cls=CommandLoader,
             context_settings={'help_option_names': ['-h', '--help'],
                               'auto_envvar_prefix': 'SLCLI',
                               'max_content_width': 999})
@click.option('--format',
              default=DEFAULT_FORMAT,
              show_default=True,
              help="Output format",
              type=click.Choice(VALID_FORMATS))
@click.option('--config', '-C',
              required=False,
              default=click.get_app_dir('softlayer', force_posix=True),
              show_default=True,
              help="Config file location",
              type=click.Path(resolve_path=True))
@click.option('--verbose', '-v',
              help="Sets the debug noise level, specify multiple times for more verbosity.",
              type=click.IntRange(0, 3, clamp=True),
              count=True)
@click.option('--proxy',
              required=False,
              help="HTTP[S] proxy to be use to make API calls")
@click.option('--really / --not-really', '-y',
              is_flag=True,
              required=False,
              help="Confirm all prompt actions")
@click.option('--demo / --no-demo',
              is_flag=True,
              required=False,
              help="Use demo data instead of actually making API calls")
@click.version_option(prog_name="slcli (SoftLayer Command-line)")
@environment.pass_env
def cli(env,
        format='table',
        config=None,
        verbose=0,
        proxy=None,
        really=False,
        demo=False,
        **kwargs):
    """Main click CLI entry-point."""

    # Populate environement with client and set it as the context object
    env.skip_confirmations = really
    env.config_file = config
    env.format = format
    env.ensure_client(config_file=config, is_demo=demo, proxy=proxy)
    env.vars['_start'] = time.time()
    logger = logging.getLogger()

    if demo is False:
        logger.addHandler(logging.StreamHandler())
    else:
        # This section is for running CLI tests.
        logging.getLogger("urllib3").setLevel(logging.WARNING)
        logger.addHandler(logging.NullHandler())

    logger.setLevel(DEBUG_LOGGING_MAP.get(verbose, logging.DEBUG))
    env.vars['_timings'] = SoftLayer.DebugTransport(env.client.transport)
    env.client.transport = env.vars['_timings']


@cli.resultcallback()
@environment.pass_env
def output_diagnostics(env, result, verbose=0, **kwargs):
    """Output diagnostic information."""

    if verbose > 0:
        diagnostic_table = formatting.Table(['name', 'value'])
        diagnostic_table.add_row(['execution_time', '%fs' % (time.time() - START_TIME)])

        api_call_value = []
        for call in env.client.transport.get_last_calls():
            api_call_value.append("%s::%s (%fs)" % (call.service, call.method, call.end_time - call.start_time))

        diagnostic_table.add_row(['api_calls', api_call_value])
        diagnostic_table.add_row(['version', consts.USER_AGENT])
        diagnostic_table.add_row(['python_version', sys.version])
        diagnostic_table.add_row(['library_location', os.path.dirname(SoftLayer.__file__)])

        env.err(env.fmt(diagnostic_table))

    if verbose > 1:
        for call in env.client.transport.get_last_calls():
            call_table = formatting.Table(['', '{}::{}'.format(call.service, call.method)])
            nice_mask = ''
            if call.mask is not None:
                nice_mask = call.mask

            call_table.add_row(['id', call.identifier])
            call_table.add_row(['mask', nice_mask])
            call_table.add_row(['filter', call.filter])
            call_table.add_row(['limit', call.limit])
            call_table.add_row(['offset', call.offset])
            env.err(env.fmt(call_table))

    if verbose > 2:
        for call in env.client.transport.get_last_calls():
            env.err(env.client.transport.print_reproduceable(call))


def main(reraise_exceptions=False, **kwargs):
    """Main program. Catches several common errors and displays them nicely."""
    exit_status = 0

    try:
        cli.main(**kwargs)
    except SoftLayer.SoftLayerAPIError as ex:
        if 'invalid api token' in ex.faultString.lower():
            print("Authentication Failed: To update your credentials, use 'slcli config setup'")
            exit_status = 1
        else:
            print(str(ex))
            exit_status = 1
    except SoftLayer.SoftLayerError as ex:
        print(str(ex))
        exit_status = 1
    except exceptions.CLIAbort as ex:
        print(str(ex.message))
        exit_status = ex.code
    except Exception:
        if reraise_exceptions:
            raise

        import traceback
        print("An unexpected error has occured:")
        print(str(traceback.format_exc()))
        print("Feel free to report this error as it is likely a bug:")
        print("    https://github.com/softlayer/softlayer-python/issues")
        print("The following snippet should be able to reproduce the error")
        exit_status = 1

    sys.exit(exit_status)


if __name__ == '__main__':
    main()
