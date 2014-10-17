"""
    SoftLayer.core
    ~~~~~~~~~~~~~~
    Core for the SoftLayer CLI

    :license: MIT, see LICENSE for more details.
"""
import logging
import sys
import time
import types

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting

import click
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
    """Loads commands for click."""
    def __init__(self, module=None, **attrs):
        click.MultiCommand.__init__(self, **attrs)
        self.module = module

    def list_commands(self, ctx):
        """Get module for click"""
        env = ctx.ensure_object(environment.Environment)
        return env.command_list(self.module)

    def get_command(self, ctx, name):
        """Get command for click"""
        env = ctx.ensure_object(environment.Environment)
        command = env.get_command(self.module, name)
        return command


class ModuleLoader(click.MultiCommand):
    """Loads module for click."""

    def list_commands(self, ctx):
        """Get module for click"""
        env = ctx.ensure_object(environment.Environment)
        return sorted(env.module_list())

    def get_command(self, ctx, name):
        """Get command for click"""
        env = ctx.ensure_object(environment.Environment)

        # Do alias lookup
        module_name = env.get_module_name(name)

        module = env.get_module(module_name)
        if isinstance(module, types.ModuleType):
            return CommandLoader(module=module_name, help=module.__doc__)
        else:
            return module


class CliClient(SoftLayer.Client):
    """ A wrapped SoftLayer.Client that adds CLI-specific functionality

    At the moment, it has a slightly different accounting for API call timings
    but will also allow for 2FA and other similar functionality.

    """

    def __init__(self, client, *args, **kwargs):
        self.real_client = client
        self.last_calls = []
        # NOTE(kmcdonald): I really don't like this pattern.

    def call(self, service, method, *args, **kwargs):
        """See Client.call for documentation."""
        start_time = time.time()

        result = self.real_client.call(service, method, *args, **kwargs)

        end_time = time.time()
        diff = end_time - start_time
        self.last_calls.append((service, method, start_time, diff))
        return result


@click.group(help="SoftLayer Command-line Client",
             epilog="""To use most commands your SoftLayer
username and api_key need to be configured. The easiest way to do that is to
use: 'sl config setup'""",
             cls=ModuleLoader)
@click.pass_context
@click.option('--format',
              default=DEFAULT_FORMAT,
              help="Output format",
              type=click.Choice(VALID_FORMATS))
@click.option('--config', '-C',
              required=False,
              default=click.get_app_dir('softlayer',
                                        force_posix=True),
              help="Config file location",
              type=click.Path(resolve_path=True))
@click.option('--debug',
              required=False,
              default='0',
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
@click.option('--really', '-y',
              is_flag=True,
              required=False,
              help="Confirm all prompt actions")
@click.option('--fixtures',
              is_flag=True,
              required=False,
              help="Use fixtures instead of actually making API calls")
@click.version_option(version=SoftLayer.__version__,
                      prog_name="SoftLayer Command-line Client")
def cli(ctx,
        format='table',
        config=None,
        debug=0,
        verbose=0,
        timings=False,
        proxy=None,
        really=False,
        fixtures=False,
        **kwargs):
    """Main click CLI entry-point"""

    # Set logging level
    debug_int = int(debug)
    if debug_int:
        verbose = debug_int

    if verbose:
        logger = logging.getLogger()
        handler = logging.StreamHandler()
        logger.addHandler(handler)
        logger.setLevel(DEBUG_LOGGING_MAP.get(verbose, logging.DEBUG))

    # Populate environement with client and set it as the context object
    env = ctx.ensure_object(environment.Environment)
    env.skip_confirmations = really
    env.config_file = config
    env.format = format
    if env.client is None:
        # Environment can be passed in explicitly. This is used for testing
        if fixtures:
            from SoftLayer import testing
            real_client = testing.FixtureClient()
        else:
            # Create SL Client
            real_client = SoftLayer.Client(proxy=proxy, config_file=config)

        client = CliClient(real_client)
        env.client = client


@cli.resultcallback()
@click.pass_context
def output_result(ctx, result, timings=False, **kwargs):
    """Outputs the results returned by the CLI and also outputs timings."""

    env = ctx.ensure_object(environment.Environment)
    output = env.fmt(result)
    if output:
        env.out(output)

    if timings:
        timing_table = formatting.KeyValueTable(['service', 'method', 'time'])

        for service, call, _, duration in env.client.last_calls:
            timing_table.add_row([service, call, duration])

        env.err(env.fmt(timing_table))


def main():
    """Main program. Catches several common errors and displays them nicely."""
    try:
        cli.main()
    except SoftLayer.SoftLayerAPIError as ex:
        if 'invalid api token' in ex.faultString.lower():
            click.echo("Authentication Failed: To update your credentials,"
                       " use 'sl config setup'")
        else:
            click.echo(str(ex))
            exit_status = 1
    except SoftLayer.SoftLayerError as ex:
        click.echo(str(ex))
        exit_status = 1
    except exceptions.CLIAbort as ex:
        click.echo(str(ex.message))
        exit_status = ex.code
    except Exception:
        import traceback
        click.echo("An unexpected error has occured:")
        click.echo(traceback.format_exc())
        click.echo("Feel free to report this error as it is likely a bug:")
        click.echo("    https://github.com/softlayer/softlayer-python/issues")
        exit_status = 1

    sys.exit(exit_status)


if __name__ == '__main__':
    main()
