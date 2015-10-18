__author__ = 'SMOKER'

import functools

__ALL_TYPES__ = {}
__ALL_INSTANCES__ = {}


class InvalidTypeException(Exception):
    def __init__(self, name):
        super(InvalidTypeException, self).__init__(name)


class DuplicateTypeException(Exception):
    def __init__(self, name):
        super(DuplicateTypeException, self).__init__(name)


def makeRegisteredType(baseType, fn):
    '''
    Takes a function, adds a new baseType subclass where the
    'create' method is the passed in fn, and returns a function
    that looks like a class constructor but actually fetches the
    instance from a cache.
    '''
    newName = fn.__name__
    if newName in __ALL_TYPES__:
        raise DuplicateTypeException(newName)

    newType = type(newName, (baseType, ), {'create': fn})
    __ALL_TYPES__[newName] = newType
    return functools.partial(getInstance, newName)


def getInstance(typeName, **kwargs):
    '''
    '''
    typeObject = __ALL_TYPES__.get(typeName)
    if not typeObject:
        raise InvalidTypeException(typeName)

    key = (typeName, tuple(kwargs.items())) # Fix this: build frozendict
    instance = __ALL_INSTANCES__.get(key)
    if instance is None:
        __ALL_INSTANCES__[key] = instance = typeObject()
        instance.create(**kwargs)
    return instance

