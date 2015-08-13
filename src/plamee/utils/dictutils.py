class sdict(dict):
    @staticmethod
    def __convert_key(key):
        return unicode(key)

    def __init__(self, iterable=None, **kwargs):
        dict.__init__(self)
        if iterable is not None:
            for key in iterable:
                value = iterable[key]
                if isinstance(value, dict):
                    value = sdict(value)
                self[key] = value
            for key in kwargs:
                value = kwargs[key]
                if isinstance(value, dict):
                    value = sdict(value)
                self[key] = value

    def copy(self):
        return sdict(self)

    def has_key(self, k):
        return self.__contains__(k)

    def get_dotted(self, key):
        fields = str(key).split(".")
        value = self
        for field in fields:
            try:
                value = value[field]
            except:
                return None
        return value

    def set_dotted(self, key, value):
        fields = str(key).split(".")
        target = self
        for field in fields[:-1]:
            target = target[field]
        target[fields[-1]] = value

    def delete_dotted(self, key):
        fields = str(key).split(".")
        target = self
        for field in fields[:-1]:
            target = target[field]
        del target[fields[-1]]

    def __contains__(self, item):
        return dict.__contains__(self, sdict.__convert_key(item))

    def __getitem__(self, item):
        return dict.__getitem__(self, sdict.__convert_key(item))

    def __setitem__(self, item, value):
        return dict.__setitem__(self, sdict.__convert_key(item), value)

    def __delitem__(self, key):
        return dict.__delitem__(self, sdict.__convert_key(key))

    def __eq__(self, other):
        if not isinstance(other, dict):
            return False
        if sorted(other.keys()) != sorted(self.keys()):
            return False
        for key in self.keys():
            if self[key] != other[key]:
                return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)


def merge_objects(obj1, obj2):
    for key in obj2.keys():
        if key in obj1 and isinstance(obj1[key], dict) and isinstance(obj2[key], dict):
            merge_objects(obj1[key], obj2[key])
        else:
            obj1[key] = obj2[key]
