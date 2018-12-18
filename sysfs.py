# https://stackoverflow.com/a/5264603/119527

from os import listdir
from os.path import isdir, isfile, islink, join, realpath, normpath
from keyword import iskeyword

_norm = lambda name: name + ('_' if iskeyword(name) else '')

def _denorm(name):
    if name.endswith('_') and iskeyword(name[:-1]):
        return name[:-1]
    else:
        return name

def _norm_path(path):
    return normpath(realpath(path))

class SysFsObject(object):
    __slots__ = ['_path', '__dict__']

    @staticmethod
    def __id_args__(path='/sys'):
        return _norm_path(path)

    def __init__(self, path='/sys'):
        self._path = _norm_path(path)
        if not self._path.startswith('/sys'):
            raise RuntimeError("Using this on non-sysfs files is dangerous!")
        self.__dict__.update(dict.fromkeys(_norm(i) for i in listdir(self._path)))

    def __repr__(self):
        return "<SysFsObject %s>" % self._path

    def __setattr__(self, name, val):
        if name.startswith('_'):
            return object.__setattr__(self, name, val)

        name = _denorm(name)

        p = realpath(join(self._path, name))
        if isfile(p):
            file(p, 'w').write(str(val))
        else:
            raise RuntimeError

    def __getattribute__(self, name):
        if name.startswith('_'):
            return object.__getattribute__(self, name)

        name = _denorm(name)

        p = realpath(join(self._path, name))
        if isfile(p):
            data = open(p, 'r').read()[:-1]
            try:
                return int(data)
            except ValueError:
                return data
        elif isdir(p):
            return SysFsObject(p)
