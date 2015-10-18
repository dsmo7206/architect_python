from maths import IDENTITY
from itertools import chain
from functools import partial
from registered_type import makeRegisteredType

class Compound(object):

    INSTANCES = {}

    def __init__(self):
        self.children = []
        self.name = self.__class__.__name__

    def add(self, obj, transform=None, **params):
        self.children.append((obj, transform, params))

    def addToGroup(self, group, transform=IDENTITY, **params):
        for childObject, childTransform, childParams in self.children:
            childObject.addToGroup(
                group,
                transform*childTransform.getMatrix() if childTransform else transform,
                **dict(chain(params.iteritems(), childParams.iteritems()))
            )

    def shallowString(self):
        return '%s with %s children (%s prims, %s triangles total)' % (
            self.name,
            len(self.children),
            self.primCount,
            self.numTriangles
        )

    def deepLines(self):
        lines = ['%s(' % self.shallowString()]
        for i, (childObject, childTransform, childParams) in enumerate(self.children):
            childLines = childObject.deepLines()
            lines.append('\tchild %s%s%s: %s' % (
                i,
                (' (%s)' % childTransform if childTransform else ''),
                (' (%s)' % ', '.join('%s=%s' % (k, v) for k, v in childParams.iteritems()) if childParams else ''),
                childLines[0]
            ))
            lines.extend('\t%s' % line for line in childLines[1:])
        lines.append(')')
        return lines

    def deepString(self):
        return '\n'.join(self.deepLines())

    @property
    def primCount(self):
        if not hasattr(self, '_primCount'):
            self._primCount = sum(child[0].primCount for child in self.children)
        return self._primCount

    @property
    def numTriangles(self):
        if not hasattr(self, '_numTriangles'):
            self._numTriangles = sum(child[0].numTriangles for child in self.children)
        return self._numTriangles


makeCompound = partial(makeRegisteredType, Compound)
