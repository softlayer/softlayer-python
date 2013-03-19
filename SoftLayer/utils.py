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

    * 'query' - exact query
    * 'query*' - prefix
    * '*query' - postfix
    * '*query*' - matches
    * '> query' '>= query' - greater-than/greater-than or equal
    * '< query' '<= query' - less-than/less-than or equal

    :param string query: query string

    """
    if isinstance(query, basestring):
        query = query.strip()
        if query.startswith('*') and query.endswith('*'):
            query = "~ %s" % query.strip('*')
        elif query.startswith('*'):
            query = "$= %s" % query.strip('*')
        elif query.endswith('*'):
            query = "^= %s" % query.strip('*')
        else:
            for op in KNOWN_OPERATIONS:
                if query.startswith(op):
                    query = "%s %s" % (op, query[len(op):].strip())
                    break

    return {'operation': query}
