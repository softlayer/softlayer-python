"""
    SoftLayer.CLI.core
    ~~~~~~~~~~~~~~~~~~
    Core for the SoftLayer CLI

    :license: MIT, see LICENSE for more details.
"""
from __future__ import print_function
import logging
import sys
import types

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting

# pylint: disable=too-many-public-methods, broad-except, unused-argument
# pylint: disable=redefined-builtin, super-init-not-called

DEBUG_LOGGING_MAP = {
    0: logging.CRITICAL,
    1: logging.WARNING,
    2: logging.INFO,
    3: logging.DEBUG
}

VALID_FORMATS = ['table', 'raw', 'json']
DEFAULT_FORMAT = 'raw'
if sys.stdout.isatty():
    DEFAULT_FORMAT = 'table'


class CommandLoader(click.MultiCommand):
    """Loads module for click."""

    def __init__(self, *path, **attrs):
        click.MultiCommand.__init__(self, **attrs)
        self.path = path

    def list_commands(self, ctx):
        """Get module for click."""
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
            return CommandLoader(*new_path, help=module.__doc__)
        else:
            return module


@click.group(help="SoftLayer Command-line Client",
             epilog="""To use most commands your SoftLayer
username and api_key need to be configured. The easiest way to do that is to
use: 'slcli setup'""",
             cls=CommandLoader,
             context_settings={'help_option_names': ['-h', '--help'],
                               'auto_envvar_prefix': 'SLCLI'})
@click.option('--format',
              default=DEFAULT_FORMAT,
              help="Output format",
              type=click.Choice(VALID_FORMATS))
@click.option('--config', '-C',
              required=False,
              default=click.get_app_dir('softlayer', force_posix=True),
              help="Config file location",
              type=click.Path(resolve_path=True))
@click.option('--debug',
              required=False,
              default=None,
              help="Sets the debug noise level",
              type=click.Choice(sorted([str(key) for key
                                        in DEBUG_LOGGING_MAP.keys()])))
@click.option('--verbose', '-v',
              help="Sets the debug noise level",
              type=click.IntRange(0, 3, clamp=True),
              count=True)
@click.option('--timings',
              required=False,
              is_flag=True,
              help="Time each API call and display after results")
@click.option('--proxy',
              required=False,
              help="HTTP[S] proxy to be use to make API calls")
@click.option('--really / --not-really', '-y',
              is_flag=True,
              required=False,
              help="Confirm all prompt actions")
@click.option('--fixtures / --no-fixtures',
              envvar='SL_FIXTURES',
              is_flag=True,
              required=False,
              help="Use fixtures instead of actually making API calls")
@click.version_option(prog_name="slcli (SoftLayer Command-line)")
@environment.pass_env
def cli(env,
        format='table',
        config=None,
        debug=0,
        verbose=0,
        proxy=None,
        really=False,
        fixtures=False,
        **kwargs):
    """Main click CLI entry-point."""

    # Set logging level
    if debug is not None:
        verbose = int(debug)

    if verbose:
        logger = logging.getLogger()
        logger.addHandler(logging.StreamHandler())
        logger.setLevel(DEBUG_LOGGING_MAP.get(verbose, logging.DEBUG))

    # Populate environement with client and set it as the context object
    env.skip_confirmations = really
    env.config_file = config
    env.format = format
    if env.client is None:
        # Environment can be passed in explicitly. This is used for testing
        if fixtures:
            client = SoftLayer.BaseClient(
                transport=SoftLayer.FixtureTransport(),
                auth=None,
            )
        else:
            # Create SL Client
            client = SoftLayer.create_client_from_env(
                proxy=proxy,
                config_file=config,
            )
        env.client = client

    env.vars['_timings'] = SoftLayer.TimingTransport(env.client.transport)
    env.client.transport = env.vars['_timings']


@cli.resultcallback()
@environment.pass_env
def output_result(env, timings=False, *args, **kwargs):
    """Outputs the results returned by the CLI and also outputs timings."""

    if timings and env.vars.get('_timings'):
        timing_table = formatting.Table(['service', 'method', 'time'])

        calls = env.vars['_timings'].get_last_calls()
        for call, _, duration in calls:
            timing_table.add_row([call.service, call.method, duration])

        env.err(env.fmt(timing_table))


def main(reraise_exceptions=False, **kwargs):
    """Main program. Catches several common errors and displays them nicely."""
    exit_status = 0

    try:
        cli.main(**kwargs)
    except SoftLayer.SoftLayerAPIError as ex:
        if 'invalid api token' in ex.faultString.lower():
            print("Authentication Failed: To update your credentials,"
                  " use 'slcli config setup'")
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
        exit_status = 1

    sys.exit(exit_status)


if __name__ == '__main__':
    main()
