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
        assert self.root and os.path.isdir(self.root)

    def __contains__(self, key):
        return self.router.route(key) and \
            os.path.lexists(self._get_path(key))

    def __getitem__(self, key):
        cls = self._get_cls(key)
        if isinstance(cls, Router):
            return Dict(self._get_path(key), cls)
        else:
            with open(self._get_path(key), 'rb') as f:
                data = f.read()
            return self._decode(data, cls)

    def _decode(self, data, cls):
        # it's already the class
        if isinstance(data, cls):
            return data
        # lots of classes seem to have this method
        if hasattr(cls, 'fromstring'):
            return cls.fromstring(data)
        # works for int, for instance
        return cls(data)

    def _get_cls(self, key):
        cls = self.router.route(key)
        if cls is None:
            raise RouterError(key)
        if key not in self:
            raise KeyError(key)
        return cls

    def _get_path(self, key):
        return os.path.join(self.root, key)

    def __delitem__(self, key):
        cls = self._get_cls(key)
        if isinstance(cls, Router):
            shutil.rmtree(self._get_path(key))
        else:
            os.unlink(self._get_path(key))

    def __setitem__(self, key, value):
        cls = self.router.route(key)
        if cls is None:
            raise RouterError(key)
        if isinstance(cls, Router) and isinstance(value, (Dict, dict)):
            if key in self:
                del self[key]
            os.mkdir(self._get_path(key))
            if len(value):
                lst = self[key]
                for k, v in value.iteritems():
                    lst[k] = v
        else:
            if not isinstance(value, cls):
                raise ValueError("%s is not a %s." % (repr(value), cls.__name__))
            data = self._encode(value, cls)
            with open(self._get_path(key), 'wb') as f:
                f.write(data)

    def _encode(self, value, cls):
        # lots of classes have this method. usually does not lose information
        if hasattr(cls, 'tostring'):
            return value.tostring()
        # no need for conversion
        if isinstance(value, basestring):
            return value
        # whitelist of classes with a __str__ that do not lose information
        if isinstance(value, (int, long)):
            return str(value)
        raise ValueError("Unable to convert %s to a string." % repr(value))

    def keys(self):
        return [f for f in os.listdir(self.root) if self.router.route(f)]

    def __iter__(self):
        return iter(self.keys())

    def __len__(self):
        return len(self.keys())
