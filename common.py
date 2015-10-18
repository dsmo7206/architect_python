import sys
import time
import maths
import pygame
import OpenGL.GL.shaders as shaders
from OpenGL import GL

PI = 3.141592653589

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 780

VERTICAL_FOV_DEGREES = 45.0

NEAR_CLIP = 0.01
FAR_CLIP = 100.0

LOOK_SPEED = 0.002
MOVE_SPEED = 3.0
ROLL_SPEED = 2.0

projMatrix = maths.perspective(
    VERTICAL_FOV_DEGREES * PI / 180.0,
    float(WINDOW_WIDTH) / float(WINDOW_HEIGHT),
    NEAR_CLIP,
    FAR_CLIP
)


def initialise():
    pygame.init()

    pygame.display.gl_set_attribute(pygame.locals.GL_MULTISAMPLEBUFFERS, 1)
    pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.OPENGL | pygame.DOUBLEBUF)
    pygame.display.set_caption('Architect')

    pygame.mouse.set_visible(False)

    GL.glClearColor(0.1, 0.1, 0.1, 1.0)
    GL.glEnable(GL.GL_DEPTH_TEST)

    GL.glEnable(GL.GL_CULL_FACE)
    GL.glCullFace(GL.GL_BACK)


def getEvents():
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            sys,exit(0)
        elif event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE:
            sys.exit(0)
    return events


def getAndResetMouse():
    mouseX, mouseY = pygame.mouse.get_pos()
    pygame.mouse.set_pos([WINDOW_WIDTH/2, WINDOW_HEIGHT/2])
    return mouseX-WINDOW_WIDTH/2, mouseY-WINDOW_HEIGHT/2


class Timer(object):
    def __init__(self, name=None):
        self.name = name
    def __enter__(self):
        self.start = time.time()
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end = time.time()
        print '%s took %.5fs' % (self.name if self.name else 'Timer', self.end - self.start)


class ShaderCompileError(Exception):
    def __init__(self, message, source, shaderType):
        self.message, self.source, self.shaderType = message, source, shaderType


def compileShaderStage(source, shaderType):
    try:
        return shaders.compileShader(source, shaderType)
    except RuntimeError as e:
        raise ShaderCompileError(e.args[0], ''.join(e.args[1]), e.args[2])

def compileShaderProgram(*stages, **named):
    try:
        return shaders.compileProgram(*stages, **named)
    except RuntimeError as e:
        print 'Error while linking shader'
        print e
        print e.__dict__