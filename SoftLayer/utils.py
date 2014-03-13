"""
    SoftLayer.utils
    ~~~~~~~~~~~~~~~
    Utility function/classes

    :license: MIT, see LICENSE for more details.
"""
import re
import six

UUID_RE = re.compile('^[0-9a-f\-]{36}$', re.I)
KNOWN_OPERATIONS = ['<=', '>=', '<', '>', '~', '!~', '*=', '^=', '$=', '_=']

configparser = six.moves.configparser  # pylint: disable=E1101
console_input = six.moves.input  # pylint: disable=E1101
string_types = six.string_types
iteritems = six.iteritems
StringIO = six.StringIO


# Code from http://stackoverflow.com/questions/11700798/python-accessing-values-nested-within-dictionaries  # NOQA
def lookup(dic, key, *keys):
    if keys:
        return lookup(dic.get(key, {}), *keys)
    return dic.get(key)


class NestedDict(dict):

    def __getitem__(self, key):
        if key in self:
            return self.get(key)
        return self.setdefault(key, NestedDict())

    def to_dict(self):
        d = {}
        for k, v in self.items():
            if isinstance(v, NestedDict):
                d[k] = v.to_dict()
            else:
                d[k] = v
        return d


def query_filter(query):
    """ Translate a query-style string to a 'filter'. Query can be the
    following formats:

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

    if isinstance(query, string_types):
        query = query.strip()
        for op in KNOWN_OPERATIONS:
            if query.startswith(op):
                query = "%s %s" % (op, query[len(op):].strip())
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


class IdentifierMixin(object):
    """ This mixin provides an interface to provide multiple methods for
        converting an 'indentifier' to an id """
    resolvers = []

    def resolve_ids(self, identifier):
        """ Takes a string and tries to resolve to a list of matching ids. What
            exactly 'identifier' can be depends on the resolvers

        :param string identifier: identifying string

        :returns list:
        """

        return resolve_ids(identifier, self.resolvers)


def resolve_ids(identifier, resolvers):
    """ Resolves IDs given a list of functions

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
