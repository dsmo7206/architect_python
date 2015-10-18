from collections import defaultdict
from OpenGL import GL
from mesh_types import NULL_PTR


class DisplayGroup(object):

    def __init__(self):
        # {program: {vao: [model_matrix]}}
        self.mapping = defaultdict(lambda: defaultdict(list))

    def addPrimitive(self, primitive, transform, params):
        self.mapping[primitive.underlying.program][primitive].append((transform, params))

    def updateUniforms(self, cameraPosition, viewMatrix, projMatrix):
        self.cameraPosition = cameraPosition
        self.viewMatrix = viewMatrix
        self.projMatrix = projMatrix

    def setModelMatrixBuffers(self):
        for program, primitiveMap in self.mapping.iteritems():
            for primitive, modelMatrixAndParamsList in primitiveMap.iteritems():
                primitive.underlying.setAttribLists(modelMatrixAndParamsList)

    def draw(self):
        for program, primitiveMap in self.mapping.iteritems():
            GL.glUseProgram(program.program)
            GL.glUniformMatrix4fv(program.uniform_vp, 1, True, self.projMatrix * self.viewMatrix)
            # Send program-level uniforms that don't vary per mesh
            GL.glUniform3f(program.uniform_eyePos, self.cameraPosition[0], self.cameraPosition[1], self.cameraPosition[2])
            for primitive, modelMatrixList in primitiveMap.iteritems():
                GL.glBindVertexArray(primitive.underlying.vao)
                # Convert this to instancing in future
                GL.glDrawElementsInstanced(GL.GL_TRIANGLES, 3*primitive.underlying.numTriangles, GL.GL_UNSIGNED_INT, NULL_PTR, len(modelMatrixList))

    def __str__(self):
        desc = []
        for program, primitiveMap in self.mapping.iteritems():
            desc.append('\tProgram %s:' % program)
            desc.extend(
                '\t\t%s: %s instances' % (primitive, len(modelMatrixList))
                for primitive, modelMatrixList in primitiveMap.iteritems()
            )
        return 'DisplayGroup(\n%s\n)' % '\n'.join(desc)


