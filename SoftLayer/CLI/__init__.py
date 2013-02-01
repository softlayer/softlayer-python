from prettytable import PrettyTable, FRAME

__all__ = [
    'CLIRunnable',
    'Table',
    'confirm',
    'no_going_back',
]

__doc__ = "CLI utilities"


class CLIRunnable():

    action = None

    @staticmethod
    def add_additional_args(parser):
        pass

    @staticmethod
    def execute(client, args):
        pass


class Table(PrettyTable):
    def __init__(self, *args, **kwargs):
        super(Table, self).__init__(*args, **kwargs)
        self.hrules = FRAME
        self.horizontal_char = '.'
        self.vertical_char = ':'
        self.junction_char = ':'


def valid_response(prompt, *valid):
    ans = raw_input(prompt).lower()

    if ans in valid:
        return True
    elif ans == '':
        return None

    return False


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
