"""
    SoftLayer.CLI.core
    ~~~~~~~~~~~~~~~~~~
    Core for the SoftLayer CLI

    :license: MIT, see LICENSE for more details.
"""
import inspect
import logging
import os
import sys
import time
import traceback
import types

import click

import requests
from rich.console import Console, RenderableType
from rich.markup import escape
from rich.text import Text
from rich.highlighter import RegexHighlighter
from rich.panel import Panel
from rich.table import Table
from rich.theme import Theme


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

PROG_NAME = "slcli (SoftLayer Command-line)"
VALID_FORMATS = ['table', 'raw', 'json', 'jsonraw']
DEFAULT_FORMAT = 'raw'

if sys.stdout.isatty():
    DEFAULT_FORMAT = 'table'


class OptionHighlighter(RegexHighlighter):
    highlights = [
        r"(?P<switch>\-\w)", # single options like -v
        r"(?P<option>\-\-[\w\-]+)", # long options like --verbose
        r"(?P<default_option>\[[^\]]+\])", # anything between [], usually default options

    ]

SLCLI_THEME = Theme(
    {
        "option": "bold cyan",
        "switch": "bold green",
        "default_option": "light_pink1",
        "option_keyword": "bold cyan",
        "args_keyword": "bold green"
    }
)

class CommandLoader(click.MultiCommand):
    """Loads module for click."""

    def __init__(self, *path, **attrs):
        click.MultiCommand.__init__(self, **attrs)
        self.path = path

        self.highlighter = OptionHighlighter()
        self.console = Console(
            theme=SLCLI_THEME
        )

    def list_commands(self, ctx):
        """List all sub-commands."""
        env = ctx.ensure_object(environment.Environment)
        env.load()

        return sorted(env.list_commands(*self.path))

    def get_command(self, ctx, cmd_name):
        """Get command for click."""
        env = ctx.ensure_object(environment.Environment)
        env.load()

        # Do alias lookup (only available for root commands)
        if len(self.path) == 0:
            cmd_name = env.resolve_alias(cmd_name)

        new_path = list(self.path)
        new_path.append(cmd_name)
        module = env.get_command(*new_path)
        if isinstance(module, types.ModuleType):
            return CommandLoader(*new_path, help=module.__doc__ or '')
        else:
            return module

    def format_usage(self, ctx: click.Context, formatter: click.formatting.HelpFormatter) -> None:
        """Formats and colorizes the usage information."""
        pieces = self.collect_usage_pieces(ctx)
        for index, piece in enumerate(pieces):
            if piece == "[OPTIONS]":
                pieces[index] = "[bold cyan][OPTIONS][/bold cyan]"
            elif piece == "COMMAND [ARGS]...":
                pieces[index] = "[orange1]COMMAND[/orange1] [bold cyan][ARGS][/bold cyan] ..."
            else:
                # print(f"OK this was {piece}")
                continue
        self.console.print(f"[bold red]{ctx.command_path}[/bold red] {' '.join(pieces)}")

    def format_help_text(self, ctx: click.Context, formatter: click.formatting.HelpFormatter) -> None:
        """Writes the help text to the formatter if it exists."""
        text = self.help if self.help is not None else ""

        if self.deprecated:
            text = _("(Deprecated) {text}").format(text=text)

        if text:
            text = inspect.cleandoc(text).partition("\f")[0]
            formatter.write_paragraph()

            with formatter.indentation():
                formatter.write_text(text)

    def format_epilog(self, ctx: click.Context, formatter: click.formatting.HelpFormatter) -> None:
        """Writes the epilog into the formatter if it exists."""
        if self.epilog:
            epilog = inspect.cleandoc(self.epilog)
            formatter.write_paragraph()

            with formatter.indentation():
                formatter.write_text(epilog)

    def format_options(self, ctx, formatter):

        options_table = Table(highlight=True, box=None, show_header=False)

        for param in self.get_params(ctx):
            if len(param.opts) == 2:
                opt1 = self.highlighter(param.opts[1])
                opt2 = self.highlighter(param.opts[0])
            else:
                opt2 = self.highlighter(param.opts[0])
                opt1 = Text("")

            # Ensures the short option is always in opt1.
            if len(opt2) == 2:
                opt1, opt2 = opt2, opt1

            if param.metavar:
                opt2 += Text(f" {param.metavar}", style="bold yellow")

            options = Text(" ".join(reversed(param.opts)))
            help_record = param.get_help_record(ctx)
            help_message = ""
            if help_record:
                help_message = param.get_help_record(ctx)[-1]

            if param.metavar:
                options += f" {param.metavar}"
            options_table.add_row(opt1, opt2, self.highlighter(help_message))

        self.console.print(options_table)
        self.format_commands(ctx, formatter)

        # click.echo(click.style('Hello World!', fg='green'))
        # print("HEEEELP")



def get_latest_version():
    """Gets the latest version of the Softlayer library."""
    try:
        result = requests.get('https://pypi.org/pypi/SoftLayer/json')
        json_result = result.json()
        latest = 'v{}'.format(json_result['info']['version'])
    except Exception:
        latest = "Unable to get version from pypi."
    return latest


CONTEXT_SETTINGS = dict(
    help_option_names=['--help', '-h'],
    auto_envvar_prefix='SLCLI',
    max_content_width=999
)
def get_version_message(ctx, param, value):
    """Gets current and latest release versions message."""
    if not value or ctx.resilient_parsing:
        return
    current = SoftLayer.consts.VERSION
    latest = get_latest_version()
    click.secho("Current: {prog} {current}\nLatest:  {prog} {latest}".format(
        prog=PROG_NAME, current=current, latest=latest))
    ctx.exit()


@click.group(help="SoftLayer Command-line Client",
             epilog="""To use most commands your SoftLayer
username and api_key need to be configured. The easiest way to do that is to
use: 'slcli setup'""",
             cls=CommandLoader,
             context_settings=CONTEXT_SETTINGS)
@click.option('--format',
              default=DEFAULT_FORMAT,
              show_default=True,
              help="Output format",
              type=click.Choice(VALID_FORMATS))
@click.option('-C',
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
              help="HTTPS or HTTP proxy to be use to make API calls")
@click.option('--really / --not-really', '-y',
              is_flag=True,
              required=False,
              help="Confirm all prompt actions")
@click.option('--demo / --no-demo',
              is_flag=True,
              required=False,
              help="Use demo data instead of actually making API calls")
@click.option('--version', is_flag=True, expose_value=False, is_eager=True, callback=get_version_message,
              help="Show version information.",  allow_from_autoenv=False,)
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

    # Populate environment with client and set it as the context object
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
    env.vars['verbose'] = verbose
    env.client.transport = env.vars['_timings']


@cli.result_callback()
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

        print("An unexpected error has occured:")
        print(str(traceback.format_exc()))
        print("Feel free to report this error as it is likely a bug:")
        print("    https://github.com/softlayer/softlayer-python/issues")
        print("The following snippet should be able to reproduce the error")
        exit_status = 1

    sys.exit(exit_status)


if __name__ == '__main__':
    main()
