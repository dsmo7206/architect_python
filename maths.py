import math
import numpy
import numpy.matlib
import operator

def Vec3(x, y, z):
    return numpy.array([x, y, z], dtype=numpy.float32)

def Vec4(x, y, z, w):
    return numpy.array([x, y, z, w], dtype=numpy.float32)

def normalise(v):
    return v / numpy.linalg.norm(v)

def zeroMatrix(size):
    return numpy.matlib.zeros(size, dtype=numpy.float32)

def identityMatrix(size):
    return numpy.matlib.identity(size, dtype=numpy.float32)

IDENTITY = identityMatrix(4)

def lookAt(position, direction, up):
    V = numpy.matlib.identity(4, dtype=numpy.float32)
    direction /= numpy.linalg.norm(direction)

    s = numpy.cross(direction, up)
    s /= numpy.linalg.norm(s)
    u = numpy.cross(s, direction)

    V[0,0:3] = s
    V[1,0:3] = u
    V[2,0:3] = -direction

    V[0,3] = -numpy.dot(s, position)
    V[1,3] = -numpy.dot(u, position)
    V[2,3] =  numpy.dot(direction, position)

    return V


class SimpleTransform(object):
    def __and__(self, other):
        if isinstance(other, CompoundTransform):
            return CompoundTransform([self] + other.transforms)
        else:
            return CompoundTransform([self, other])


class CompoundTransform(object):
    def __init__(self, transforms):
        self.transforms = transforms
    def getMatrix(self):
        return reduce(operator.mul, (t.getMatrix() for t in self.transforms))
    def __and__(self, other):
        if isinstance(other, CompoundTransform):
            return CompoundTransform(self.transforms + other.transforms)
        else:
            return CompoundTransform(self.transforms + [other])
    def __repr__(self):
        return ', '.join(repr(t) for t in self.transforms)


class Translate(SimpleTransform):
    def __init__(self, x, y, z):
        self.x, self.y, self.z = x, y, z
    def getMatrix(self):
        return numpy.matrix(
            [
                [ 1, 0, 0, self.x],
                [ 0, 1, 0, self.y],
                [ 0, 0, 1, self.z],
                [ 0, 0, 0,      1]
            ],
            dtype=numpy.float32
        )

    def __repr__(self):
        return 'Translate(%s, %s, %s)' % (self.x, self.y, self.z)


class Scale(SimpleTransform):
    def __init__(self, x, y, z):
        self.x, self.y, self.z = x, y, z
    def getMatrix(self):
        return numpy.matrix(
            [
                [self.x,      0,      0, 0],
                [     0, self.y,      0, 0],
                [     0,      0, self.z, 0],
                [     0,      0,      0, 1]
            ],
            dtype=numpy.float32
        )
    def __repr__(self):
        return 'Scale(%s, %s, %s)' % (self.x, self.y, self.z)


class RotateX(SimpleTransform):
    def __init__(self, angle):
        self.angle = angle

    def getMatrix(self):
        cosT, sinT = math.cos(self.angle), math.sin(self.angle)
        return numpy.matrix(
            [
                [1.0,  0.0,   0.0, 0.0],
                [0.0, cosT, -sinT, 0.0],
                [0.0, sinT,  cosT, 0.0],
                [0.0,  0.0,   0.0, 1.0]
            ],
            dtype=numpy.float32
        )

    def __repr__(self):
        return 'RotateX(%s)' % self.angle


class RotateY(SimpleTransform):
    def __init__(self, angle):
        self.angle = angle

    def getMatrix(self):
        cosT, sinT = math.cos(self.angle), math.sin(self.angle)
        return numpy.matrix(
            [
                [ cosT, 0.0, sinT, 0.0],
                [ 0.0,  1.0,  0.0, 0.0],
                [-sinT, 0.0, cosT, 0.0],
                [ 0.0,  0.0,  0.0, 1.0]
            ],
            dtype=numpy.float32
        )

    def __repr__(self):
        return 'RotateY(%s)' % self.angle


class RotateZ(SimpleTransform):
    def __init__(self, angle):
        self.angle = angle

    def getMatrix(self):
        cosT, sinT = math.cos(self.angle), math.sin(self.angle)
        return numpy.matrix(
            [
                [cosT, -sinT, 0.0, 0.0],
                [sinT,  cosT, 0.0, 0.0],
                [ 0.0,   0.0, 1.0, 0.0],
                [ 0.0,   0.0, 0.0, 1.0]
            ],
            dtype=numpy.float32
        )

    def __repr__(self):
        return 'RotateZ(%s)' % self.angle


class Rotate(SimpleTransform):
    def __init__(self, angle, axis):
        self.angle = angle
        axis = normalise(axis)
        self.x, self.y, self.z = axis[0], axis[1], axis[2]

    def getMatrix(self):
        c, s = math.cos(self.angle), math.sin(self.angle)
        cx, cy, cz = (1-c)*self.x, (1-c)*self.y, (1-c)*self.z
        return numpy.matrix(
            [
                [       cx*self.x + c, cy*self.x - self.z*s, cz*self.x + self.y*s, 0.0],
                [cx*self.y + self.z*s,        cy*self.y + c, cz*self.y - self.x*s, 0.0],
                [cx*self.z - self.y*s, cy*self.z + self.x*s,        cz*self.z + c, 0.0],
                [                 0.0,                  0.0,                  0.0, 1.0]
            ],
            dtype=numpy.float32
        )

    def __repr__(self):
        return 'Rotate(angle=%s, axis=(%s, %s, %s))' % (self.angle, self.x, self.y, self.z)

'''

def ortho(left, right, bottom, top, znear, zfar):
    assert right  != left
    assert bottom != top
    assert znear  != zfar

    M = zeroMatrix((4,4), dtype=np.float32)
    M[0,0] = +2.0/(right-left)
    M[3,0] = -(right+left)/float(right-left)
    M[1,1] = +2.0/(top-bottom)
    M[3,1] = -(top+bottom)/float(top-bottom)
    M[2,2] = -2.0/(zfar-znear)
    M[3,2] = -(zfar+znear)/float(zfar-znear)
    M[3,3] = 1.0
    return M

def frustum(left, right, bottom, top, znear, zfar):
    assert right  != left
    assert bottom != top
    assert znear  != zfar

    M = zeroMatrix((4,4), dtype=np.float32)
    M[0,0] = +2.0*znear/(right-left)
    M[2,0] = (right+left)/(right-left)
    M[1,1] = +2.0*znear/(top-bottom)
    M[3,1] = (top+bottom)/(top-bottom)
    M[2,2] = -(zfar+znear)/(zfar-znear)
    M[3,2] = -2.0*znear*zfar/(zfar-znear)
    M[2,3] = -1.0
    return M
'''

def perspective(fovy, ar, n, f):
    h = 1.0 / math.tan(0.5 * fovy)
    return numpy.matrix(
        [
            [ h / ar, 0.0,               0.0,                     0.0],
            [    0.0,   h,               0.0,                     0.0],
            [    0.0, 0.0, (f + n) / (n - f), (2.0 * f * n) / (n - f)],
            [    0.0, 0.0,              -1.0,                     0.0]
        ],
        dtype=numpy.float32
    )

class Quaternion(object):
    def __init__(self, w, x, y, z):
        self.w = w
        self.x = x
        self.y = y
        self.z = z

    @staticmethod
    def angleAxis(angle, axis):
        halfAngle = 0.5 * angle
        halfSin = math.sin(halfAngle)
        return Quaternion(math.cos(halfAngle), axis[0] * halfSin, axis[1] * halfSin, axis[2] * halfSin)

    def __mul__(self, other):
        if isinstance(other, numpy.ndarray) and other.shape == (3,):
            qv = Vec3(self.x, self.y, self.z)
            uv = numpy.cross(qv, other)
            uuv = numpy.cross(qv, uv)
            uv *= (2.0 * self.w)
            uuv *= 2.0
            return other + uv + uuv
        elif isinstance(other, Quaternion):
            return Quaternion(
                self.w*other.w - self.x*other.x - self.y*other.y - self.z*other.z,
                self.w*other.x + self.x*other.w + self.y*other.z - self.z*other.y,
                self.w*other.y + self.y*other.w + self.z*other.x - self.x*other.z,
                self.w*other.z + self.z*other.w + self.x*other.y - self.y*other.x
            )
        else:
            assert False

    def __str__(self):
        return 'Quaternion(w=%s, x=%s, y=%s, z=%s)' % (self.w, self.x, self.y, self.z)

