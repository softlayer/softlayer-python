

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
