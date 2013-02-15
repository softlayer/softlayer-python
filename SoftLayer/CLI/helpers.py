
from SoftLayer.CLI.environment import CLIRunnableType
from prettytable import PrettyTable

__all__ = ['Table', 'CLIRunnable', 'FormattedItem', 'valid_response',
           'add_really_argument', 'confirm', 'no_going_back', 'mb_to_gb',
           'listing']


class FormattedItem(object):
    def __init__(self, original, formatted=None):
        self.original = original
        if formatted:
            self.formatted = formatted
        else:
            self.formatted = self.original

    def __str__(self):
        return str(self.original)

    __repr__ = __str__


def mb_to_gb(megabytes):
    return FormattedItem(megabytes, "%dG" % (float(megabytes) / 1024))


def listing(item, separator=','):
    l = separator.join((str(i) for i in item))
    return FormattedItem(l, l)


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
    def __init__(self, msg, *args):
        super(CLIAbort, self).__init__(code=2, *args)
        self.message = msg


class Table(object):
    def __init__(self, columns):
        self.columns = columns
        self.rows = []
        self.align = {}
        self.format = {}
        self.sortby = None

    def add_row(self, row):
        self.rows.append(row)

    def prettytable(self):
        " Returns a new prettytable instance"
        t = PrettyTable(self.columns)
        if self.sortby:
            t.sortby = self.sortby
        for a_col, alignment in self.align.items():
            t.align[a_col] = alignment

        # Adding rows
        for row in self.rows:
            t.add_row(row)
        return t
