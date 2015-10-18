import maths
import numpy
import pygame
import common

class InputStatus(object):
    def __init__(self):
        self.moveLeftPressed = 0
        self.moveRightPressed = 0
        self.moveFwdPressed = 0
        self.moveBackPressed = 0
        self.moveUpPressed = 0
        self.moveDownPressed = 0
        self.rollLeftPressed = 0
        self.rollRightPressed = 0
        self.mouseDx = 0
        self.mouseDy = 0
    def handleEvents(self, events):
        unhandledEvents = []
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_w:
                self.moveFwdPressed = 1
            elif event.type == pygame.KEYUP and event.key == pygame.K_w:
                self.moveFwdPressed = 0
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_s:
                self.moveBackPressed = 1
            elif event.type == pygame.KEYUP and event.key == pygame.K_s:
                self.moveBackPressed = 0
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_a:
                self.moveLeftPressed = 1
            elif event.type == pygame.KEYUP and event.key == pygame.K_a:
                self.moveLeftPressed = 0
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_d:
                self.moveRightPressed = 1
            elif event.type == pygame.KEYUP and event.key == pygame.K_d:
                self.moveRightPressed = 0
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                self.rollLeftPressed = 1
            elif event.type == pygame.KEYUP and event.key == pygame.K_q:
                self.rollLeftPressed = 0
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                self.rollRightPressed = 1
            elif event.type == pygame.KEYUP and event.key == pygame.K_e:
                self.rollRightPressed = 0
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                self.moveUpPressed = 1
            elif event.type == pygame.KEYUP and event.key == pygame.K_r:
                self.moveUpPressed = 0
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_f:
                self.moveDownPressed = 1
            elif event.type == pygame.KEYUP and event.key == pygame.K_f:
                self.moveDownPressed = 0
            else:
                unhandledEvents.append(event)
        return unhandledEvents

class Camera(object):
    def __init__(self, position, direction, up):
        self.position = position
        self.direction = direction
        self.up = up
        self.viewMatrix = maths.lookAt(self.position, self.direction, self.up)

    def update(self, dt, inputStatus):
        lookDx = common.LOOK_SPEED * inputStatus.mouseDx
        lookDy = common.LOOK_SPEED * inputStatus.mouseDy

        lookDYaw = common.ROLL_SPEED * (inputStatus.rollLeftPressed - inputStatus.rollRightPressed) * dt

        right = numpy.cross(self.direction, self.up)

        totalQuat = (
            maths.Quaternion.angleAxis(-lookDy, right) *
            maths.Quaternion.angleAxis(-lookDx, self.up) *
            maths.Quaternion.angleAxis(-lookDYaw, self.direction)
        )

        # Update self
        self.up = totalQuat * self.up
        self.direction = totalQuat * self.direction

        self.position += dt * common.MOVE_SPEED * (
            (inputStatus.moveFwdPressed - inputStatus.moveBackPressed) * self.direction +
            (inputStatus.moveRightPressed - inputStatus.moveLeftPressed) * right +
            (inputStatus.moveUpPressed - inputStatus.moveDownPressed) * self.up
        )

        # Update the view matrix
        self.viewMatrix = maths.lookAt(self.position, self.direction, self.up)

    def __str__(self):
        return 'Camera(position=%s, direction=%s, up=%s)' % (self.position, self.direction, self.up)