KNOWN_OPERATIONS = ['<=', '>=', '<', '>', '~', '*=', '^=', '$=', '_=', '!~']


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
      'value'   Exact value match
      'value*'  Begins with value
      '*value'  Ends with value
      '*value*' Contains value

    Case Sensitive
      '~ value'   Exact value match
      '> value'   Greater than value
      '< value'   Less than value
      '>= value'  Greater than or equal to value
      '<= value'  Less than or equal to value

    :param string query: query string

    """
    if isinstance(query, basestring):
        query = query.strip()
        for op in KNOWN_OPERATIONS:
            if query.startswith(op):
                query = "%s %s" % (op, query[len(op):].strip())
                return {'operation': query}
        if query.startswith('*') and query.endswith('*'):
            query = "~ %s" % query.strip('*')
        elif query.startswith('*'):
            query = "$= %s" % query.strip('*')
        elif query.endswith('*'):
            query = "^= %s" % query.strip('*')
        else:
            query = "_= %s" % query

    return {'operation': query}
