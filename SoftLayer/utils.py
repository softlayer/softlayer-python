"""
    SoftLayer.utils
    ~~~~~~~~~~~~~~~
    Utility function/classes.

"""

import collections
import datetime
from json import JSONDecoder
import re
import time

from rich.console import Console
from rich.theme import Theme
from SoftLayer.CLI import exceptions
# pylint: disable=no-member, invalid-name

UUID_RE = re.compile(r'^[0-9A-F]{8}-[0-9A-F]{4}-4[0-9A-F]{3}-[89AB][0-9A-F]{3}-[0-9A-F]{12}$', re.I)
KNOWN_OPERATIONS = ['<=', '>=', '<', '>', '~', '!~', '*=', '^=', '$=', '_=']


def lookup(dic, key, *keys):
    """A generic dictionary access helper.

    This helps simplify code that uses heavily nested dictionaries. It will
    return None if any of the keys in `*keys` do not exist.

    ::

        >>> lookup({'this': {'is': 'nested'}}, 'this', 'is')
        nested

        >>> lookup({}, 'this', 'is')
        None

    """
    if keys:
        return lookup(dic.get(key, {}), keys[0], *keys[1:])
    return dic.get(key)


class NestedDict(dict):
    """This helps with accessing a heavily nested dictionary.

    Dictionary where accessing keys that don't exist will return another
    NestedDict object.

    """

    def __getitem__(self, key):
        if key in self:
            return self.get(key)
        return self.setdefault(key, NestedDict())

    def to_dict(self):
        """Converts a NestedDict instance into a real dictionary.

        This is needed for places where strict type checking is done.
        """
        return {key: val.to_dict() if isinstance(val, NestedDict) else val
                for key, val in self.items()}


def dict_merge(dct1, dct2):
    """Recursively merges dct2 and dct1, ideal for merging objectFilter together.

    :param dct1: A dictionary
    :param dct2: A dictionary
    :return: dct1 + dct2
    """

    dct = dct1.copy()
    for k, _ in dct2.items():
        if (k in dct1 and isinstance(dct1[k], dict) and isinstance(dct2[k], collections.abc.Mapping)):
            dct[k] = dict_merge(dct1[k], dct2[k])
        else:
            dct[k] = dct2[k]
    return dct


def query_filter(query):
    """Translate a query-style string to a 'filter'.

    Query can be the following formats:

    Case Insensitive
      'value' OR '*= value'    Contains
      'value*' OR '^= value'   Begins with value
      '*value' OR '$= value'   Ends with value
      '*value*' OR '_= value'  Contains value

    Case Sensitive
      '~ value'   Contains
      '!~ value'  Does not contain
      '> value'   Greater than value
      '< value'   Less than value
      '>= value'  Greater than or equal to value
      '<= value'  Less than or equal to value

    :param string query: query string

    """
    try:
        return {'operation': int(query)}
    except ValueError:
        pass

    if isinstance(query, str):
        query = query.strip()
        for operation in KNOWN_OPERATIONS:
            if query.startswith(operation):
                query = "%s %s" % (operation, query[len(operation):].strip())
                return {'operation': query}
        if query.startswith('*') and query.endswith('*'):
            query = "*= %s" % query.strip('*')
        elif query.startswith('*'):
            query = "$= %s" % query.strip('*')
        elif query.endswith('*'):
            query = "^= %s" % query.strip('*')
        else:
            query = "_= %s" % query

    return {'operation': query}


def query_filter_date(start, end):
    """Query filters given start and end date.

    :param start:YY-MM-DD
    :param end: YY-MM-DD
    """
    sdate = datetime.datetime.strptime(start, "%Y-%m-%d")
    edate = datetime.datetime.strptime(end, "%Y-%m-%d")
    startdate = "%s/%s/%s" % (sdate.month, sdate.day, sdate.year)
    enddate = "%s/%s/%s" % (edate.month, edate.day, edate.year)
    return {
        'operation': 'betweenDate',
        'options': [
            {'name': 'startDate', 'value': [startdate + ' 0:0:0']},
            {'name': 'endDate', 'value': [enddate + ' 0:0:0']}
        ]
    }


def query_filter_orderby(sort="ASC"):
    """Returns an object filter operation for sorting

    :param string sort: either ASC or DESC
    """
    _filter = {
        "operation": "orderBy",
        "options": [{
            "name": "sort",
            "value": [sort]
        }]
    }
    return _filter


def format_event_log_date(date_string, utc):
    """Gets a date in the format that the SoftLayer_EventLog object likes.

    :param string date_string: date in mm/dd/yyyy format
    :param string utc: utc offset. Defaults to '+0000'
    """
    user_date_format = "%m/%d/%Y"

    user_date = datetime.datetime.strptime(date_string, user_date_format)
    dirty_time = user_date.isoformat()

    if utc is None:
        utc = "+0000"

    iso_time_zone = utc[:3] + ':' + utc[3:]
    cleaned_time = "{}.000000{}".format(dirty_time, iso_time_zone)

    return cleaned_time


def event_log_filter_between_date(start, end, utc):
    """betweenDate Query filter that SoftLayer_EventLog likes

    :param string start: lower bound date in mm/dd/yyyy format
    :param string end: upper bound date in mm/dd/yyyy format
    :param string utc: utc offset. Defaults to '+0000'
    """
    return {
        'operation': 'betweenDate',
        'options': [
            {'name': 'startDate', 'value': [format_event_log_date(start, utc)]},
            {'name': 'endDate', 'value': [format_event_log_date(end, utc)]}
        ]
    }


def event_log_filter_greater_than_date(date, utc):
    """greaterThanDate Query filter that SoftLayer_EventLog likes

    :param string date: lower bound date in mm/dd/yyyy format
    :param string utc: utc offset. Defaults to '+0000'
    """
    return {
        'operation': 'greaterThanDate',
        'options': [
            {'name': 'date', 'value': [format_event_log_date(date, utc)]}
        ]
    }


def event_log_filter_less_than_date(date, utc):
    """lessThanDate Query filter that SoftLayer_EventLog likes

    :param string date: upper bound date in mm/dd/yyyy format
    :param string utc: utc offset. Defaults to '+0000'
    """
    return {
        'operation': 'lessThanDate',
        'options': [
            {'name': 'date', 'value': [format_event_log_date(date, utc)]}
        ]
    }


def build_filter_orderby(orderby):
    """Builds filters using the filter options passed into the CLI.

    It only supports the orderBy option, the default value is DESC.
    """
    _filters = {}
    reverse_filter = list(reversed(orderby.split('.')))
    for keyword in reverse_filter:
        _aux_filter = {}
        if '=' in keyword:
            _aux_filter[str(keyword).split('=', maxsplit=1)[0]] = query_filter_orderby(str(keyword).split('=')[1])
            _filters = _aux_filter
        elif keyword == list(reverse_filter)[0]:
            _aux_filter[keyword] = query_filter_orderby('DESC')
        else:
            _aux_filter[keyword] = _filters
        _filters = _aux_filter
    return _filters


class IdentifierMixin(object):
    """Mixin used to resolve ids from other names of objects.

    This mixin provides an interface to provide multiple methods for
    converting an 'indentifier' to an id
    """
    resolvers = []

    def resolve_ids(self, identifier):
        """Takes a string and tries to resolve to a list of matching ids.

        What exactly 'identifier' can be depends on the resolvers

        :param string identifier: identifying string
        :returns list:
        """

        return resolve_ids(identifier, self.resolvers)


def resolve_ids(identifier, resolvers):
    """Resolves IDs given a list of functions.

    :param string identifier: identifier string
    :param list resolvers: a list of functions
    :returns list:
    """

    # Before doing anything, let's see if this is an integer
    try:
        return [int(identifier)]
    except ValueError:
        pass  # It was worth a shot

    # This looks like a globalIdentifier (UUID)
    if len(identifier) == 36 and UUID_RE.match(identifier):
        return [identifier]

    for resolver in resolvers:
        ids = resolver(identifier)
        if ids:
            return ids

    return []


class UTC(datetime.tzinfo):
    """UTC timezone."""

    def utcoffset(self, _):
        return datetime.timedelta(0)

    def tzname(self, _):
        return "UTC"

    def dst(self, _):
        return datetime.timedelta(0)


def is_ready(instance, pending=False):
    """Returns True if instance is ready to be used

    :param Object instance: Hardware or Virt with transaction data retrieved from the API
    :param bool pending: Wait for ALL transactions to finish?
    :returns bool:
    """

    last_reload = lookup(instance, 'lastOperatingSystemReload', 'id')
    active_transaction = lookup(instance, 'activeTransaction', 'id')

    reloading = all((
        active_transaction,
        last_reload,
        last_reload == active_transaction,
    ))
    outstanding = False
    if pending:
        outstanding = active_transaction
    if instance.get('provisionDate') and not reloading and not outstanding:
        return True
    return False


def clean_string(string):
    """Returns a string with all newline and other whitespace garbage removed.

    Mostly this method is used to print out objectMasks that have a lot of extra whitespace
    in them because making compact masks in python means they don't look nice in the IDE.

    :param string: The string to clean.
    :returns string: A string without extra whitespace.
    """
    if string is None:
        return ''
    else:
        return " ".join(string.split())


def clean_splitlines(string):
    """Returns a string where \r\n is replaced with \n"""
    if string is None:
        return ''
    else:
        return "\n".join(string.splitlines())


def clean_time(sltime, in_format='%Y-%m-%dT%H:%M:%S%z', out_format='%Y-%m-%d %H:%M'):
    """Easy way to format time strings

    :param string sltime: A softlayer formatted time string
    :param string in_format: Datetime format for strptime
    :param string out_format: Datetime format for strftime
    """
    if sltime is None:
        return None
    try:
        clean = datetime.datetime.strptime(sltime, in_format)
        return clean.strftime(out_format)
    # The %z option only exists with py3.6+
    except ValueError as e:
        # Just ignore data that in_format didn't process.
        ulr = len(e.args[0].partition('unconverted data remains: ')[2])
        if ulr:
            clean = datetime.datetime.strptime(sltime[:-ulr], in_format)
            return clean.strftime(out_format)
        return sltime


def verify_date(date):
    """Verify if the date format is correct

    :param string date: A date in format string
    :return Exception: a exception if the date is not the correct format
    """
    try:
        date = datetime.datetime.strptime(date, '%m/%d/%Y')
    except Exception as exc:
        raise exceptions.CLIAbort('Date invalid, example date: mm/dd/yyyy, 01/15/2023.') from exc


def timestamp(date):
    """Converts a datetime to timestamp

    :param datetime date:
    :returns int: The timestamp of date.
    """

    _timestamp = time.mktime(date.timetuple())

    return int(_timestamp)


def days_to_datetime(days):
    """Returns the datetime value of last N days.

    :param int days: From 0 to N days
    :returns int: The datetime of last N days or datetime.now() if days <= 0.
    """

    date = datetime.datetime.now()

    if days > 0:
        date -= datetime.timedelta(days=days)

    return date


def trim_to(string, length=80, tail="..."):
    """Returns a string that is length long. tail added if trimmed

    :param string string: String you want to trim
    :param int length: max length for the string
    :param string tail: appended to strings that were trimmed.
    """

    if len(string) > length:
        return string[:length] + tail
    else:
        return string


def format_comment(comment, max_line_length=60):
    """Return a string that is length long, added a next line and keep the table format.

    :param string comment: String you want to add next line
    :param int max_line_length: max length for the string
    """
    comment_length = 0
    words = comment.split(" ")
    formatted_comment = ""
    for word in words:
        if comment_length + (len(word) + 1) <= max_line_length:
            formatted_comment = formatted_comment + word + " "

            comment_length = comment_length + len(word) + 1
        else:
            formatted_comment = formatted_comment + "\n" + word + " "

            comment_length = len(word) + 1
    return formatted_comment


def clean_dict(dictionary):
    """Removes any `None` entires from the dictionary"""
    return {k: v for k, v in dictionary.items() if v}


NOT_WHITESPACE = re.compile(r'[^\s]')


def decode_stacked(document, pos=0, decoder=JSONDecoder()):
    """Used for converting CLI output to JSON datastructures. Specially for unit tests

    https://stackoverflow.com/questions/27907633/how-to-extract-multiple-json-objects-from-one-file

    Example::

        split_output = []
        # Converts Rich JSON output to actual JSON data. JSON UTIL
        for table in utils.decode_stacked(result.output):
            split_output.append(table)
    """
    while True:
        match = NOT_WHITESPACE.search(document, pos)
        if not match:
            return
        pos = match.start()
        obj, pos = decoder.raw_decode(document, pos)

        yield obj


def console_color_themes(theme):
    """Colors in https://rich.readthedocs.io/en/stable/appendix/colors.html?highlight=light_pink1#standard-colors"""

    if theme == 'light':
        return Console(theme=Theme(
            {
                "options": "bold dark_cyan",  # OPTIONS
                "command": "orange3",  # COMMAND
                "args": "bold dark_cyan",  # ARGS
                "path": "bold red",  # command path
                "name_sub_command": "orange3",  # sub command name
                "sub_command": "orange3",  # sub command list
                # Help table colors options
                "option": "bold dark_cyan",
                "switch": "bold green4",
                "default_option": "light_coral",
                "option_keyword": "bold dark_cyan",
                "args_keyword": "bold green4",
                "option_choices": "gold3",
            })
        )
    return Console(theme=Theme(
        {
            "options": "bold cyan",  # OPTIONS
            "command": "orange3",  # COMMAND
            "args": "bold cyan",  # ARGS
            "path": "bold red",  # command path
            "name_sub_command": "orange3",  # sub command name
            "sub_command": "orange3",  # sub command list
            # Help table colors options
            "option": "bold cyan",
            "switch": "bold green",
            "default_option": "light_pink1",
            "option_keyword": "bold cyan",
            "args_keyword": "bold green",
            "option_choices": "gold3",
        })
    )


def table_color_theme(theme):
    """Define result table colors"""
    if theme == 'light':
        return {'header': 'dark_cyan',
                'id_columns': 'light_coral'}
    return {'header': 'bright_cyan',
            'id_columns': 'pale_violet_red1'}
