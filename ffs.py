from collections import Mapping  # TODO MutableMapping
import os
from fnmatch import fnmatchcase


class RouterError(Exception):
    def __init__(self, key):
        Exception.__init__(self, "%s does not match any route." % key)


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
            if fnmatchcase(key, pattern):
                return cls


class List(Mapping):
    def __init__(self, root, router):
        self.root = root
        self.router = router

    def __contains__(self, key):
        return self.router.route(key) and \
            os.path.lexists(os.path.join(self.root, key))

    def __getitem__(self, key):
        cls = self.router.route(key)
        if cls is None:
            raise RouterError(key)
        if key not in self:
            raise KeyError(key)
        if isinstance(cls, Router):
            return List(os.path.join(self.root, key), cls)
        else:
            with open(os.path.join(self.root, key), 'r') as f:
                data = f.read()
            if hasattr(cls, 'fromstring'):
                return cls.fromstring(data)
            return cls(data)

    def keys(self):
        return [f for f in os.listdir(self.root) if self.router.route(f)]

    def __iter__(self):
        return iter(self.keys())

    def __len__(self):
        return len(self.keys())
