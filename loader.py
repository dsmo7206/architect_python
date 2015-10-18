import math
import maths
import random
import common
import compound
import primitives
import registered_type


class MissingMainException(Exception):
    pass


def loadObjectFromFile(filename):
    with open(filename, 'r') as f:
        source = f.read()
    return loadObjectFromSource(source)

def loadObjectFromSource(source):

    myDict = {
        'primitive': primitives.makePrimitive,
        'compound': compound.makeCompound,
        'math': math,
        'maths': maths,
        'r': random.random,
        'getInstance': registered_type.getInstance,
        'VertexPrimitive': primitives.VertexPrimitive,
        'VertexNormalPrimitive': primitives.VertexNormalPrimitive,
    }

    with common.Timer('Parsing source'):
        exec source in myDict

    main = myDict.get('main')
    if not main:
        raise MissingMainException()

    with common.Timer('Building objects'):
        return myDict['main']()

def loadObjectFromModule(moduleName):
    module = __import__(moduleName)
    if not hasattr(module, 'main'):
        raise MissingMainException()

    return module.main()
