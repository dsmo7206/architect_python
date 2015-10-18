import OpenGL
OpenGL.ERROR_CHECKING = True
OpenGL.FULL_LOGGING = False

import pygame
import pygame.locals
import OpenGL.GL as GL
import common
import maths
import camera
import display_group
import traceback, sys

from shaders import BlinnWithNormalsProgram
from shaders import BlinnWithoutNormalsProgram

def testLoadedGroup():
    group = display_group.DisplayGroup()
    import loader
    #obj = loader.loadObjectFromFile('data.py')
    obj = loader.loadObjectFromModule('data')
    obj.addToGroup(
        group,
        maths.Scale(0.3, 0.3, 0.3).getMatrix(),
        ambient=maths.Vec3(0.0, 0.0, 0.0),
        diffuse=maths.Vec3(1.5, 0.5, 0.5),
        specular=maths.Vec4(0.0, 1.0, 1.0, 32.0),
    )
    return group

def main():

    common.initialise()

    startTime = pygame.time.get_ticks()
    lastElapsed = 0

    inputStatus = camera.InputStatus()
    cam = camera.Camera(
        maths.Vec3( 0.0,  0.0, 10.0), # eye
        maths.Vec3( 0.0,  0.0, -1.0), # direction
        maths.Vec3( 0.0,  1.0,  0.0), # up
    )

    common.getAndResetMouse()

    group = testLoadedGroup()
    group.setModelMatrixBuffers()

    lightDir = (0.5, 0.5, 0.5) # TOWARDS the light

    # Set up colours
    for program in (
        BlinnWithoutNormalsProgram.get(),
        BlinnWithNormalsProgram.get()
    ):
        GL.glUseProgram(program.program)
        GL.glUniform3f(program.uniform_lightDir, *lightDir) # TOWARDS the light


    while True:
        # Recalculate from inputs
        events = common.getEvents()
        inputStatus.handleEvents(events)

        inputStatus.mouseDx, inputStatus.mouseDy = common.getAndResetMouse()

        elapsed = 0.001 * (pygame.time.get_ticks() - startTime)
        cam.update(elapsed - lastElapsed, inputStatus)
        lastElapsed = elapsed

        group.updateUniforms(cam.position, cam.viewMatrix, common.projMatrix)

        # Clear and redraw
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        group.draw()

        pygame.display.flip()

CATCHING_EXCEPTIONS = True

def handleException(e):
    excType, excValue, excTraceback = sys.exc_info()
    if isinstance(e, common.ShaderCompileError):
        print('Error while compiling shader stage: %s at' % e.shaderType)
        print(''.join(traceback.format_tb(excTraceback)))
        print(e.message)
        print('Source:')
        print(e.source)
    else:
        print(''.join(traceback.format_exception(excType, excValue, excTraceback)))

if __name__ == '__main__':
    if CATCHING_EXCEPTIONS:
        try:
            main()
        except Exception as e:
            handleException(e)
        finally:
            pygame.quit()
    else:
        try:
            main()
        finally:
            pygame.quit()