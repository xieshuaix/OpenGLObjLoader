# Basic OBJ file viewer. needs objloader from:
#  http://www.pygame.org/wiki/OBJFileLoader
# LMB + move: rotate
# RMB + move: pan
# Scroll wheel: zoom in/out
# Assume there is a .mtl file with the same name as .obj file
import sys
import pygame
from pygame.locals import *
from pygame.constants import *
from OpenGL.GL import *
from OpenGL.GLU import *

# IMPORT OBJECT LOADER
from loadObj import *

pygame.init()
# This specified window size
viewport = (500, 500)
hx = viewport[0] / 2
hy = viewport[1] / 2
srf = pygame.display.set_mode(viewport, OPENGL | DOUBLEBUF)


glEnable(GL_LIGHTING)
glEnable(GL_LIGHT1)  # Include i lights in calculation for GL_LIGHTi
glEnable(GL_DEPTH_TEST)
glClear(GL_DEPTH_BUFFER_BIT)
# What are these?
glEnable(GL_COLOR_MATERIAL)
glShadeModel(GL_SMOOTH)  # most obj files expect to be smooth-shaded
# Set light source properties
glLightfv(GL_LIGHT1, GL_POSITION, (-40, 200, 100, 0.0))  # Set position of light source in homogeneous coordinate
glLightfv(GL_LIGHT1, GL_AMBIENT, (0.2, 0.2, 0.2, 1.0))  # Set ambient RGBA intensity of light
glLightfv(GL_LIGHT1, GL_DIFFUSE, (0.5, 0.5, 0.5, 1.0))  # Set diffuse RGBA intensity of light
# Set material properties for lighting calculation
glMaterialfv(GL_FRONT, GL_AMBIENT, [0, 0, 0, 0])  # Set ambient reflectance
glMaterialfv(GL_FRONT, GL_DIFFUSE, [0.5, 0.75, 1.0, 0.0])  # Set diffuse reflectance
glMaterialf(GL_FRONT, GL_SHININESS, 0.25*128.0)  # Set specular exponent, or shininess

# LOAD OBJECT AFTER PYGAME INIT
obj = OBJ(sys.argv[1], swapyz=True)

clock = pygame.time.Clock()  # This creats a clock, which can be used to track time spent on frames, not used.

glMatrixMode(GL_PROJECTION)
glLoadIdentity()  # Set the current matrix (operation) to identity matrix, effectively resetting transformation.
width, height = viewport
# Set camera view range
# input: fovy, aspect, zNear, zFar
zNear = 1.0
zFar = 100.0
gluPerspective(90.0, width / float(height), zNear, zFar)
# Set camera position, aiming direction and upward direction
# input: eye position/camera position, look at point(tells where to aim), upward direction
# If this this disabled, default camera posision will be at (0,0,0), and default upward direction will be (0,1,0)
# gluLookAt(0.0, 0.0, 5.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0)
glEnable(GL_DEPTH_TEST)
glMatrixMode(GL_MODELVIEW)

# Retrieve mouse motion and set how graphics will update.
rx, ry = (0, 0)  # Rotation
tx, ty = (0, 0)  # Translation
zpos = 6  # This is just a parameter controlling step size in z position of camera when zooming. It is not a position.
rotate = move = False
while 1:
    clock.tick(30)  # Limit frame rate to lower than 30 per second
    for e in pygame.event.get():
        if e.type == QUIT:
            sys.exit()
        elif e.type == KEYDOWN and e.key == K_ESCAPE:
            sys.exit()
        elif e.type == MOUSEBUTTONDOWN:
            if e.button == 4:  # Scroll up to zoom in
                zpos = max(zNear, zpos - 1)  # Limits camera position to in front of zNear
                print(zpos)
            elif e.button == 5:  # Scroll down to zoom out
                zpos = min(zFar, zpos + 1)  # Limits camera position to in front of zFar
                print(zpos)
            elif e.button == 1:  # Left click enables rotation
                rotate = True
            elif e.button == 3:  # Right click enables panning
                move = True
        elif e.type == MOUSEBUTTONUP:
            if e.button == 1:
                rotate = False
            elif e.button == 3:
                move = False
        elif e.type == MOUSEMOTION:
            i, j = e.rel  # Displacement of mouse
            if rotate:
                rx += i
                ry += j
            if move:
                tx += i
                ty -= j

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    # Reset matrix operation before applying new ones, otherwise operations stack and update for current iteration will
    # depend on previous updates
    glLoadIdentity()

    # RENDER OBJECT (updated)
    # The dot below indicates a float. This transform camera position, so to zoom in, you have to move in negative
    # z direction
    glTranslate(tx / 20., ty / 20., - zpos)
    glRotate(ry, 1, 0, 0)  # (angle,x,y,z), rotate camera by ry about x-axis
    glRotate(rx, 0, 1, 0)  # (angle,x,y,z), rotate camera by ry about y-axis
    glCallList(obj.gl_list)

    pygame.display.flip()