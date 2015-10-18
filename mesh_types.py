import numpy
import ctypes
import itertools
import OpenGL.GL as GL
from shaders.blinn_with_normals import BlinnWithNormalsProgram
from shaders.blinn_without_normals import BlinnWithoutNormalsProgram


SIZE_OF_FLOAT32 = 4
SIZE_OF_UNSIGNED32 = 4
list_sum = lambda iterable: sum(iterable, [])
NULL_PTR = ctypes.c_void_p(0)


class BlinnShadedMesh(object):

    def __del__(self):
        pass # Should delete GL objects

    def setAttribLists(self, attribLists):
        GL.glBindVertexArray(self.vao)

        # Build one buffer for each non-position attribute
        # that our program needs
        self.ambientBuffer, self.diffuseBuffer, self.specularBuffer, self.modelMatrixBuffer = GL.glGenBuffers(4)

        # Set up ambient
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.ambientBuffer)
        GL.glBufferData(
            GL.GL_ARRAY_BUFFER,
            len(attribLists) * SIZE_OF_FLOAT32 * 3,
            numpy.concatenate([m[1]['ambient'] for m in attribLists]).astype(numpy.float32, copy=False),
            GL.GL_STATIC_DRAW
        )
        GL.glEnableVertexAttribArray(self.program.attrib_ambient)
        GL.glVertexAttribPointer(self.program.attrib_ambient, 3, GL.GL_FLOAT, False, 3*SIZE_OF_FLOAT32, ctypes.c_void_p(0))
        GL.glVertexAttribDivisor(self.program.attrib_ambient, 1)

        # Set up diffuse
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.diffuseBuffer)
        GL.glBufferData(
            GL.GL_ARRAY_BUFFER,
            len(attribLists) * SIZE_OF_FLOAT32 * 3,
            numpy.concatenate([m[1]['diffuse'] for m in attribLists]).astype(numpy.float32, copy=False),
            GL.GL_STATIC_DRAW
        )
        GL.glEnableVertexAttribArray(self.program.attrib_diffuse)
        GL.glVertexAttribPointer(self.program.attrib_diffuse, 3, GL.GL_FLOAT, False, 3*SIZE_OF_FLOAT32, ctypes.c_void_p(0))
        GL.glVertexAttribDivisor(self.program.attrib_diffuse, 1)

        # Set up specular
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.specularBuffer)
        GL.glBufferData(
            GL.GL_ARRAY_BUFFER,
            len(attribLists) * SIZE_OF_FLOAT32 * 4,
            numpy.concatenate([m[1]['specular'] for m in attribLists]).astype(numpy.float32, copy=False),
            GL.GL_STATIC_DRAW
        )
        GL.glEnableVertexAttribArray(self.program.attrib_specular)
        GL.glVertexAttribPointer(self.program.attrib_specular, 4, GL.GL_FLOAT, False, 4*SIZE_OF_FLOAT32, ctypes.c_void_p(0))
        GL.glVertexAttribDivisor(self.program.attrib_specular, 1)

        # Set up model matrix
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.modelMatrixBuffer)
        GL.glBufferData(
            GL.GL_ARRAY_BUFFER,
            len(attribLists) * SIZE_OF_FLOAT32 * 16,
            numpy.concatenate([m[0].T for m in attribLists]).astype(numpy.float32, copy=False),
            GL.GL_STATIC_DRAW
        )
        for i in range(4):
            GL.glEnableVertexAttribArray(self.program.attrib_m + i)
            GL.glVertexAttribPointer(
                self.program.attrib_m + i,
                4,
                GL.GL_FLOAT,
                False,
                16*SIZE_OF_FLOAT32,
                ctypes.c_void_p(i * 4 * SIZE_OF_FLOAT32)
            )
            GL.glVertexAttribDivisor(self.program.attrib_m + i, 1)
        GL.glBindVertexArray(0)


class VertexMesh(BlinnShadedMesh):
    def __init__(self, name, vertices, indices):
        self.name = name

        assert len(indices) % 3 == 0
        self.numTriangles = len(indices) / 3

        vertex_data = vertices if isinstance(vertices, numpy.ndarray) else numpy.concatenate(vertices)
        index_data = numpy.array(indices, dtype=numpy.uint32)

        self.vao = GL.glGenVertexArrays(1)
        GL.glBindVertexArray(self.vao)

        self.vbo, self.ibo = GL.glGenBuffers(2)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.ibo)

        self.program = BlinnWithoutNormalsProgram.get()

        GL.glEnableVertexAttribArray(self.program.attrib_position)
        GL.glVertexAttribPointer(self.program.attrib_position, 3, GL.GL_FLOAT, False, 3*SIZE_OF_FLOAT32, ctypes.c_void_p(0))

        # Send the data over to the buffer
        GL.glBufferData(GL.GL_ARRAY_BUFFER, len(vertex_data) * SIZE_OF_FLOAT32, vertex_data.astype(numpy.float32, copy=False), GL.GL_STATIC_DRAW)
        GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER, len(index_data) * SIZE_OF_UNSIGNED32, index_data, GL.GL_STATIC_DRAW)

        # Unbind the VAO first (Important)
        GL.glBindVertexArray(0)

        # Unbind other stuff
        GL.glDisableVertexAttribArray(self.program.attrib_position)
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, 0)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)

    def __str__(self):
        return '%s(VertexPrimitive, vao=%s, %s triangles)' % (
            self.name, self.vao, self.numTriangles
        )


class VertexNormalMesh(BlinnShadedMesh):
    def __init__(self, name, vertices, normals, indices):
        self.name = name
        assert len(vertices) == len(normals)

        assert len(indices) % 3 == 0
        self.numTriangles = len(indices) / 3

        vertex_data = numpy.array(
            list_sum(
                [v[0], v[1], v[2], n[0], n[1], n[2]]
                for v, n
                in itertools.izip(vertices, normals)
            ),
            dtype=numpy.float32
        )

        index_data = numpy.array(indices, dtype=numpy.uint32)

        self.vao = GL.glGenVertexArrays(1)
        GL.glBindVertexArray(self.vao)

        self.vbo, self.ibo = GL.glGenBuffers(2)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.ibo)

        self.program = BlinnWithNormalsProgram.get()

        GL.glEnableVertexAttribArray(self.program.attrib_position)
        GL.glEnableVertexAttribArray(self.program.attrib_normal)

        GL.glVertexAttribPointer(self.program.attrib_position, 3, GL.GL_FLOAT, False, 6*SIZE_OF_FLOAT32, ctypes.c_void_p(0))
        GL.glVertexAttribPointer(self.program.attrib_normal,   3, GL.GL_FLOAT, False, 6*SIZE_OF_FLOAT32, ctypes.c_void_p(3*SIZE_OF_FLOAT32))

        # Send the data over to the buffer
        GL.glBufferData(GL.GL_ARRAY_BUFFER, len(vertex_data) * SIZE_OF_FLOAT32, vertex_data, GL.GL_STATIC_DRAW)
        GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER, len(index_data) * SIZE_OF_UNSIGNED32, index_data, GL.GL_STATIC_DRAW)

        # Unbind the VAO first (Important)
        GL.glBindVertexArray(0)

        # Unbind other stuff
        GL.glDisableVertexAttribArray(self.program.attrib_normal)
        GL.glDisableVertexAttribArray(self.program.attrib_position)
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, 0)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)

    def __str__(self):
        return 'VertexNormalPrimitive(vao=%s, %s triangles)' % (
            self.vao, self.numTriangles
        )


