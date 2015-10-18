import math
import numpy
import os
from primitives import makePrimitive
from compound import makeCompound
from maths import Vec3
from registered_type import getInstance
from mesh_types import VertexMesh, VertexNormalMesh
from maths import Translate, RotateX
from random import random as r

@makePrimitive
def Cube(self, **kwargs):
    self.underlying = VertexMesh(
        'Cube',
        [
            Vec3(0.0, 0.0, 0.0), # Left bottom back (0)
            Vec3(0.0, 0.0, 1.0), # Left bottom front (1)
            Vec3(0.0, 1.0, 0.0), # Left top back (2)
            Vec3(0.0, 1.0, 1.0), # Left top front (3)
            Vec3(1.0, 0.0, 0.0), # Right bottom back (4)
            Vec3(1.0, 0.0, 1.0), # Right bottom front (5)
            Vec3(1.0, 1.0, 0.0), # Right top back (6)
            Vec3(1.0, 1.0, 1.0), # Right top front (7)
        ],
        [
            1, 5, 7, 7, 3, 1, # Front
            3, 7, 6, 6, 2, 3, # Top
            0, 1, 3, 3, 2, 0, # Left
            5, 4, 6, 6, 7, 5, # Right
            4, 0, 2, 2, 6, 4, # Back
            0, 4, 5, 5, 1, 0, # Bottom
        ]
    )

@makePrimitive
def Quad(self, **kwargs):
    self.underlying = VertexNormalMesh(
        'Quad',
        [Vec3(0.0, 0.0, 0.0), Vec3(1.0, 0.0, 0.0), Vec3(1.0, 1.0, 0.0), Vec3(0.0, 1.0, 0.0)],
        [Vec3(0.0, 0.0, 1.0), Vec3(0.0, 0.0, 1.0), Vec3(0.0, 0.0, 1.0), Vec3(0.0, 0.0, 1.0)],
        [0, 1, 2, 2, 3, 0]
    )

@makePrimitive
def Brick(self, **kwargs):
    x_size = kwargs['x_size']
    y_size = kwargs['y_size']
    x_rows = kwargs['x_rows']
    y_rows = kwargs['y_rows']
    max_bump = kwargs['max_bump']

    # Make front face
    all_x = numpy.concatenate([numpy.linspace(0.0, x_size, x_rows, dtype=numpy.float32)] * y_rows)
    all_x += numpy.clip(numpy.random.normal(scale=0.7*max_bump, size=x_rows*y_rows), -max_bump, max_bump)

    all_y = numpy.concatenate(numpy.meshgrid(range(x_rows), numpy.linspace(0.0, y_size, y_rows, dtype=numpy.float32))[1])
    all_y += numpy.clip(numpy.random.normal(scale=0.7*max_bump, size=x_rows*y_rows), -max_bump, max_bump)

    all_z = numpy.zeros((x_rows*y_rows,), dtype=numpy.float32)
    all_z += numpy.clip(numpy.random.normal(scale=0.7*max_bump, size=x_rows*y_rows), -max_bump, max_bump)

    # Interleave
    vertices = numpy.vstack((all_x, all_y, all_z)).reshape((-1,), order='F')

    # Make indexes
    indices = []
    for y_row in range(y_rows - 1):
        row_start_index = x_rows * y_row
        for x_row in range(x_rows - 1):
            this_index = row_start_index + x_row
            indices.extend([this_index, this_index + 1, this_index + x_rows, this_index + x_rows, this_index + 1, this_index + x_rows + 1])

    self.underlying = VertexMesh('Brick', vertices, indices)


@makePrimitive
def WavefrontPrimitive(**kwargs):
    filename = kwargs['filename']
    usingNormals = kwargs.get('normals', False)

    # Add dummy elements because indices in file start with 1
    vertices, indices = [Vec3(0.0, 0.0, 0.0)], []

    if usingNormals:
        normals, comboMap = [Vec3(0.0, 0.0, 0.0)], {} # Unique (vertex, normal): index map

    with open(filename, 'r') as f:
        for line in f:
            lineSplit = line.split(' ')
            lineType = lineSplit[0]
            if lineType == 'vn' and usingNormals:
                normals.append(Vec3(*lineSplit[1:]))
            elif lineType == 'v':
                vertices.append(Vec3(*lineSplit[1:]))
            elif lineType == 'f':
                assert len(lineSplit) == 4
                face = [part.split('/') for part in lineSplit[1:]]
                if usingNormals:
                    for f in face:
                        indices.append(comboMap.setdefault((int(f[0]), int(f[2])), len(comboMap)))
                else:
                    indices.extend(f[0] for f in face)

    name = os.path.split(filename)[-1]

    if usingNormals:
        newVertices = [Vec3(0.0, 0.0, 0.0)] * len(comboMap)
        newNormals = [Vec3(0.0, 0.0, 0.0)] * len(comboMap)

        for (vertexIndex, normalIndex), newIndex in comboMap.iteritems():
            newVertices[newIndex] = vertices[vertexIndex]
            newNormals[newIndex] = normals[normalIndex]

        return VertexNormalMesh(name, newVertices, newNormals, indices)
    else:
        return VertexMesh(name, vertices, indices)


@makeCompound
def Cube2(self):
    self.add(getInstance('Cube'), RotateX(0.5))

@makeCompound
def BritishFlag(self, **kwargs):
    obj = getInstance('Cube')

    height, width = kwargs['height'], 2 * kwargs['height']
    spacing = kwargs.get('spacing', 1.1)

    redDiagIntDist, redDiagDist = (height/30.0) / math.cos(math.atan(0.5)), height/30.0

    def lineDist(x, y, grad, intercept):
        return abs(-grad*x + y - intercept) / math.sqrt(grad*grad + 1.0)

    inRange = lambda x, lower, upper: x >= lower and x <= upper

    def middleRed(x, y):
        return inRange(x*60, 27*width, 32*width) or inRange(y*30, 12*height, 17*height)

    def middleWhite(x, y):
        return (
            (x*60 >= 25*width and x*60 <= 34*width) or
            (y*30 >= 10*height and y*30 <= 19*height)
        )

    def diagWhite(x, y):
        return min(lineDist(x, y, 0.5, 0.0), lineDist(x, y, -0.5, height)) <= 0.1 * height

    def diagRed(x, y):
        if x <= 0.5*width and y <= 0.5*height: # Bottom left
            return lineDist(x, y, 0.5, -redDiagIntDist) <= redDiagDist
        elif x <= 0.5*width: # Top left
            return lineDist(x, y, -0.5, height-redDiagIntDist) <= redDiagDist
        elif y <= 0.5*height: # Bottom right
            return lineDist(x, y, -0.5, height+redDiagIntDist) <= redDiagDist
        else: # Top right
            return lineDist(x, y, 0.5, redDiagIntDist) <= redDiagDist

    red = Vec3(204.0/256.0, 0.0, 0.0)
    white = Vec3(1.0, 1.0, 1.0)
    blue = Vec3(0.0, 0.0, 102.0/256.0)

    for _x in range(width):
        for _y in range(height):
            x, y = _x + 0.5, _y + 0.5
            if middleRed(x, y):     diffuse, bumpHeight = red, 0.3
            elif middleWhite(x, y): diffuse, bumpHeight = white, 0.1
            elif diagRed(x, y):     diffuse, bumpHeight = red, 0.3
            elif diagWhite(x, y):   diffuse, bumpHeight = white, 0.1
            else:                   diffuse, bumpHeight = blue, 0.2
            self.add(obj, Translate(spacing*_x, spacing*_y, bumpHeight*r()), diffuse=diffuse)

@makeCompound
def BrickWall(self, **kwargs):
    brick = getInstance('Cube')
    #brick = standard_primitives.WavefrontPrimitive.get(filename='meshes/plisson.obj')
    for y in range(30):
        for x in range(30):
            self.add(brick, Translate(x*1.1, y*1.1, 0.0))

@makeCompound
def BrickWallCollection(self, **kwargs):
    wall = BrickWall()
    for z in range(30):
        self.add(wall, Translate(0.0, 0.0, z * 1.1))

@makeCompound
def Suburbia(self, **kwargs):
    house = getInstance('WavefrontPrimitive', filename='meshes/plisson.obj')

    for x in range(10):
        for z in range(10):
            if x == 3:
                self.add(house, Translate(20.0*x, 0.0, 20.0*z), diffuse=Vec3(1.0, 0.0, 0.0))
            elif z == 4:
                self.add(house, Translate(20.0*x, 0.0, 20.0*z), diffuse=Vec3(0.0, 0.0, 1.0))
            else:
                self.add(house, Translate(20.0*x, 0.0, 20.0*z))

@makePrimitive
def BasicHouseRoof(self, **kwargs):
    sizeX = kwargs['sizeX'] # Width
    sizeZ = kwargs['sizeZ'] # Depth
    gradient = kwargs['gradient']

    name = 'BasicHouseRoof'

    if sizeX == sizeZ:
        size = sizeX
        vertices = [
            Vec3(0.0, 0.0, 0.0),
            Vec3(size, 0.0, 0.0),
            Vec3(size, 0.0, -size),
            Vec3(0.0, 0.0, -size),
            Vec3(0.5*size, gradient*0.5*size, -0.5*size)
        ]
        indices = [0, 1, 4, 1, 2, 4, 2, 3, 4, 3, 0, 4, 2, 1, 0, 0, 3, 2]
    else:
        if sizeX > sizeZ:
            apexDist = 0.5 * sizeZ
            vertices = [
                Vec3(0.0, 0.0, 0.0),
                Vec3(sizeX, 0.0, 0.0),
                Vec3(sizeX, 0.0, -sizeZ),
                Vec3(0.0, 0.0, -sizeZ),
                Vec3(apexDist, gradient*apexDist, -apexDist),
                Vec3(sizeX-apexDist, gradient*apexDist, -apexDist)
            ]
            indices = [0, 1, 4, 4, 1, 5, 1, 2, 5, 2, 3, 5, 5, 3, 4, 3, 0, 4, 2, 1, 0, 0, 3, 2]
        else: # sizeZ > sizeX
            apexDist = 0.5 * sizeX
            vertices = [
                Vec3(0.0, 0.0, 0.0),
                Vec3(sizeX, 0.0, 0.0),
                Vec3(sizeX, 0.0, -sizeZ),
                Vec3(0.0, 0.0, -sizeZ),
                Vec3(apexDist, gradient*apexDist, -apexDist),
                Vec3(apexDist, gradient*apexDist, -(sizeZ-apexDist))
            ]
            indices = [0, 1, 4, 1, 2, 4, 4, 2, 5, 2, 3, 5, 3, 0, 5, 5, 0, 4, 2, 1, 0, 0, 3, 2]
    self.underlying = VertexMesh(name, vertices, indices)

@makeCompound
def House(self, **kwargs):
    sizeX = kwargs['sizeX'] # Width
    sizeZ = kwargs['sizeZ'] # Depth

    roof = BasicHouseRoof(sizeX=sizeX, sizeZ=sizeZ, gradient=1.3)
    self.add(roof)
    return

    bodyDepth = sizeZ
    bodyWidth = 0.3 * sizeZ
    if sizeX > bodyWidth:
        sideWidth = 0.5 * (sizeX - bodyWidth)
    else:
        sideWidth = 0

    print 'sideWidth: %s' % sideWidth

    from random import random as r
    # Stretch rand [0,1] to [1,2]
    heightMult = r() + 1.0
    bodyHeight = bodyWidth * heightMult

    quad = getInstance('Quad')

    # Add grass
    self.add(
        quad,
        maths.RotateX(-0.5*math.pi) & maths.Scale(sizeX, sizeZ, 1.0),
        diffuse=(0,1,0)
    )

    cube = getInstance('Cube')

    self.add(
        cube,
        maths.Translate(0.0, 0.5*bodyHeight, 0.0) & maths.Scale(bodyWidth, bodyHeight, bodyDepth)
    )

    if sideWidth:
        sideDepth = sideWidth
        self.add(
            cube,
            maths.Translate(-bodyWidth+0.5*sideWidth, 0.5*bodyHeight, 0.0) & maths.Scale(sideWidth, bodyHeight, sideDepth)
        )
        self.add(
            cube,
            maths.Translate(bodyWidth-0.5*sideWidth, 0.5*bodyHeight, 0.0) & maths.Scale(sideWidth, bodyHeight, sideDepth)
        )

def main():
    #return BritishFlag(height=120, spacing=1.1)
    return getInstance('BritishFlag', height=120, spacing=1.1)
    #return getInstance('Quad')
    return getInstance('House', sizeX=20.0, sizeZ=80.0)
