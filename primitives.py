import registered_type
import functools
from maths import IDENTITY


class Primitive(object):
    primCount = 1

    def addToGroup(self, group, transform=IDENTITY, **params):
        group.addPrimitive(self, transform, params)

    def deepLines(self):
        return [str(self)]


makePrimitive = functools.partial(registered_type.makeRegisteredType, Primitive)

