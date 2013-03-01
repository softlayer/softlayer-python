
from SoftLayer.CLI.environment import CLIRunnableType
from prettytable import PrettyTable

__all__ = ['Table', 'CLIRunnable', 'FormattedItem', 'valid_response',
           'confirm', 'no_going_back', 'mb_to_gb', 'listing', 'CLIAbort']


class FormattedItem(object):
    def __init__(self, original, formatted=None):
        self.original = original
        if formatted is not None:
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
    options = []
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


def confirm(prompt_str, default=False):
    if default:
        prompt = '%s [Y/n]: ' % prompt_str
    else:
        prompt = '%s [y/N]: ' % prompt_str

    response = valid_response(prompt, 'y', 'yes', 'yeah', 'yup', 'yolo')

    if response is None:
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


class ArgumentError(CLIAbort):
    def __init__(self, msg, *args):
        super(CLIAbort, self).__init__(code=2, *args)
        self.message = "Argument Error: %s" % msg


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


class SequentialOutput(list):
    def __init__(self, blanks=True, *args, **kwargs):
        self.blanks = blanks


class NestedDict(dict):

    def __getitem__(self, key):
        if key in self:
            return self.get(key)
        return self.setdefault(key, NestedDict())
