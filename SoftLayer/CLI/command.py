import click
import types
import inspect

from rich import box
from rich.console import Console, RenderableType
from rich.markup import escape
from rich.text import Text
from rich.highlighter import RegexHighlighter
from rich.panel import Panel
from rich.table import Table
from rich.theme import Theme


from SoftLayer.CLI import environment

class OptionHighlighter(RegexHighlighter):
    highlights = [
        r"(?P<switch>\-\w)", # single options like -v
        r"(?P<option>\-\-[\w\-]+)", # long options like --verbose
        r"(?P<default_option>\[[^\]]+\])", # anything between [], usually default options

    ]

# Colors defined in https://rich.readthedocs.io/en/latest/_modules/rich/color.html#ColorType
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

        self.console.print(f"Usage: [bold red]{ctx.command_path}[/bold red] {' '.join(pieces)}")

    def format_help_text(self, ctx: click.Context, formatter: click.formatting.HelpFormatter) -> None:
        """Writes the help text"""
        text = self.help if self.help is not None else ""

        if self.deprecated:
            text = _("(Deprecated) {text}").format(text=text)

        if text:
            text = inspect.cleandoc(text).partition("\f")[0]
        self.console.print(f"\n\t{text}\n")

    def format_epilog(self, ctx: click.Context, formatter: click.formatting.HelpFormatter) -> None:
        """Writes the epilog if it exists, then prints out any sub-commands if they exist."""
        if self.epilog:
            epilog = inspect.cleandoc(self.epilog)
            epilog = epilog.replace("\n", " ")
            self.console.print(epilog)
        self.format_commands(ctx, formatter)


    def format_options(self, ctx, formatter):
        """Prints out the options in a table format"""

        options_table = Table(highlight=True, box=box.SQUARE, show_header=False)

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

    def format_commands(self, ctx, formatter):
        commands = []
        for subcommand in self.list_commands(ctx):
            cmd = self.get_command(ctx, subcommand)
            # What is this, the tool lied about a command.  Ignore it
            if cmd is None or cmd.hidden:
                continue
            commands.append((subcommand, cmd))

        command_table = Table(highlight=True, box=None, show_header=False)
        if len(commands):
            for subcommand, cmd in commands:
                help_text = cmd.get_short_help_str(120)
                command_style = Text(f" {subcommand}", style="orange1")
                command_table.add_row(command_style, help_text)
        self.console.print("\n[bold orange1]Commands:[/]")
        self.console.print(command_table)

class SLCommand(click.Command):
    """Overloads click.Command to control how the help message is formatted."""

    def __init__(self, *path, **attrs):
        click.Command.__init__(self, **attrs)
        self.highlighter = OptionHighlighter()
        self.console = Console(
            theme=SLCLI_THEME
        )


    def format_usage(self, ctx: click.Context, formatter: click.formatting.HelpFormatter) -> None:
        """Formats and colorizes the usage information."""
        pieces = self.collect_usage_pieces(ctx)
        for index, piece in enumerate(pieces):
            if piece == "[OPTIONS]":
                pieces[index] = "[bold cyan][OPTIONS][/bold cyan]"
            elif piece == "COMMAND [ARGS]...":
                pieces[index] = "[orange1]COMMAND[/orange1] [bold cyan][ARGS][/bold cyan] ..."

        self.console.print(f"Usage: [bold red]{ctx.command_path}[/bold red] {' '.join(pieces)}")

    def format_help_text(self, ctx: click.Context, formatter: click.formatting.HelpFormatter) -> None:
        """Writes the help text"""
        text = self.help if self.help is not None else ""

        if self.deprecated:
            text = _("(Deprecated) {text}").format(text=text)

        if text:
            text = inspect.cleandoc(text)

        self.console.print(f"\n\t{text}\n")

    def format_epilog(self, ctx: click.Context, formatter: click.formatting.HelpFormatter) -> None:
        """Writes the epilog if it exists, then prints out any sub-commands if they exist."""
        if self.epilog:
            epilog = inspect.cleandoc(self.epilog)
            epilog = epilog.replace("\n", " ")
            self.console.print(epilog)

    def format_options(self, ctx, formatter):
        """Prints out the options in a table format"""

        ## TODO support binary options --yes/--no
        ## SUPPORT color for IDENTIFIER and such
        options_table = Table(highlight=True, box=box.SQUARE, show_header=False)

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
