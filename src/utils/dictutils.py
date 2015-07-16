class sdict(dict):
    def __init__(self, iterable=None, **kwargs):
        if not iterable:
            iterable = dict()
        dict.__init__(self, iterable, **kwargs)
        for key in self.keys():
            if isinstance(self[key], dict):
                self[key] = sdict(self[key])

    def copy(self):
        return sdict(self)

    def has_key(self, k):
        return self.__contains__(k)

    def __contains__(self, item):
        return dict.__contains__(self, str(item))

    def __getitem__(self, item):
        return dict.__getitem__(self, str(item))

    def __setitem__(self, item, value):
        return dict.__setitem__(self, str(item), value)


def merge_objects(obj1, obj2):
    for key in obj2.keys():
        if key in obj1 and isinstance(obj1[key], dict) and isinstance(obj2[key], dict):
            merge_objects(obj1[key], obj2[key])
        else:
            obj1[key] = obj2[key]
