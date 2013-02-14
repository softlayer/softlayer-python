
from SoftLayer.CLI.environment import CLIRunnableType
from prettytable import PrettyTable

__all__ = ['Table', 'CLIRunnable', 'valid_response', 'add_really_argument',
           'confirm', 'no_going_back']


class CLIRunnable(object):
    __metaclass__ = CLIRunnableType
    action = None

    @staticmethod
    def add_additional_args(parser):
        pass

    @staticmethod
    def execute(client, args):
        pass


def valid_response(prompt, *valid):
    ans = raw_input(prompt).lower()

    if ans in valid:
        return True
    elif ans == '':
        return None

    return False


def add_really_argument(parser):
    parser.add_argument(
        '--really', '-y',
        help='Confirm all prompt actions',
        action='store_true',
        default=False)


def confirm(prompt_str="", allow_empty=False, default=False):
    fmt = (prompt_str, 'y', 'n') if default else (prompt_str, 'n', 'y')
    if allow_empty:
        prompt = '%s [%s]|%s: ' % fmt
    else:
        prompt = '%s %s|%s: ' % fmt

    response = valid_response(prompt, 'y', 'yes')

    if response is None and allow_empty:
        return default

    return response


def no_going_back(confirmation):
    if not confirmation:
        confirmation = 'yes'

    return valid_response(
        'This action cannot be undone! '
        'Type in "%s" or press Enter to abort.' % confirmation,
        confirmation)


class CLIHalt(SystemExit):
    def __init__(self, code=0, *args):
        super(CLIHalt, self).__init__(*args)
        self.code = code


class CLIAbort(CLIHalt):
    def __init__(self, *args):
        super(CLIAbort, self).__init__(code=2, *args)


class Table(object):
    def __init__(self, columns):
        self.columns = columns
        self.rows = []
        self.align = {}
        self.format = {}
        self.sortby = None

    def add_row(self, row, **kwargs):
        self.rows.append(TableRow(row, **kwargs))

    def _col_format_mapping(self):
        " Generate mapping of column index to formatter for that column "
        format_col_map = {}
        for col, fmter in self.format.items():
            if col in self.columns:
                format_col_map[self.columns.index(col)] = fmter
        return format_col_map

    def prettytable(self, format=True):
        " Returns a new prettytable instance"
        t = PrettyTable(self.columns)
        if format and self.sortby:
            t.sortby = self.sortby
        if format:
            for a_col, alignment in self.align.items():
                t.align[a_col] = alignment

            # Generate mapping of column_id to formatter
            format_col_map = self._col_format_mapping()
        # Adding rows
        for row in self.rows:
            _row = list(row.items)

            if format:
                # format based on column formatters
                for fmt_i, fmter in row.formatters.items():
                    _row[fmt_i] = fmter(_row[fmt_i])

                # format based on row-specific formatters
                for fmt_i, fmter in format_col_map.items():
                    _row[fmt_i] = fmter(_row[fmt_i])

            t.add_row(_row)
        return t


class TableRow(object):
    def __init__(self, items, formatters=None):
        self.items = items
        self.formatters = formatters or {}
