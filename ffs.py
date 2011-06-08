from collections import MutableMapping
import os
from fnmatch import fnmatchcase
import shutil


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


class Dict(MutableMapping):
    def __init__(self, root, router):
        self.root = root
        self.router = router

    def __contains__(self, key):
        return self.router.route(key) and \
            os.path.lexists(self._get_path(key))

    def __getitem__(self, key):
        cls = self._get_cls(key)
        if self._is_dict(cls):
            return Dict(self._get_path(key), cls)
        else:
            with open(self._get_path(key), 'rb') as f:
                data = f.read()
            if hasattr(cls, 'fromstring'):
                return cls.fromstring(data)
            return cls(data)

    def _get_cls(self, key):
        cls = self.router.route(key)
        if cls is None:
            raise RouterError(key)
        if key not in self:
            raise KeyError(key)
        return cls

    def _is_dict(self, cls):
        return isinstance(cls, Router)

    def _get_path(self, key):
        return os.path.join(self.root, key)

    def __delitem__(self, key):
        cls = self._get_cls(key)
        if self._is_dict(cls):
            shutil.rmtree(self._get_path(key))
        else:
            os.unlink(self._get_path(key))

    def __setitem__(self, key, value):
        cls = self.router.route(key)
        if cls is None:
            raise RouterError(key)
        if not isinstance(value, cls):
            raise ValueError("%s is not a %s." % (repr(value), cls.__name__))
        if hasattr(cls, 'tostring'):
            data = value.tostring()
        elif isinstance(value, basestring):
            data = value
        else:
            raise ValueError("Unable to convert %s to a string." % repr(value))
        with open(self._get_path(key), 'wb') as f:
            f.write(data)

    def keys(self):
        return [f for f in os.listdir(self.root) if self.router.route(f)]

    def __iter__(self):
        return iter(self.keys())

    def __len__(self):
        return len(self.keys())
