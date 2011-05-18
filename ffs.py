from collections import Mapping  # TODO MutableMapping
import os


class RouterError(Exception):
    pass


class Router(object):
    def __init__(self, _advroutes=None, **routes):
        if _advroutes is None:
            _advroutes = {}
        routes.update(_advroutes)
        self.routes = []
        for pattern, cls in routes.iteritems():
            self.register(pattern, cls)

    def register(self, pattern, cls):
        self.routes.append((pattern, cls))

    def route(self, key):
        for pattern, cls in self.routes:
            if key == pattern:
                return cls
        raise RouterError("No type found for %s" % key)


class List(Mapping):
    def __init__(self, root, router):
        self.root = root
        self.router = router

    def __contains__(self, key):
        return os.path.lexists(os.path.join(self.root, key))

    def __getitem__(self, key):
        if key not in self:
            raise KeyError(key)
        cls = self.router.route(key)
        if isinstance(cls, Router):
            return List(os.path.join(self.root, key), cls)
        else:
            with open(os.path.join(self.root, key), 'r') as f:
                data = f.read()
            if hasattr(cls, 'fromstring'):
                return cls.fromstring(data)
            return cls(data)

    def keys(self):
        return os.listdir(self.root)

    def __iter__(self):
        return iter(self.keys())

    def __len__(self):
        return len(self.keys())
