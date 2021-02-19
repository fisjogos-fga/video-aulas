import pyxel
from math import sqrt
import random

x, y = 90, -10
radius = 5
velocity = 2
paused = True


def update():
    global x, y, velocity, paused

    if paused and pyxel.btnp(pyxel.MOUSE_LEFT_BUTTON):
        paused = False
        x += random.uniform(-70, 70)

    if not paused and pyxel.btnp(pyxel.MOUSE_LEFT_BUTTON):
        dx = pyxel.mouse_x - x
        dy = pyxel.mouse_y - y
        if sqrt(dx ** 2 + dy ** 2) < radius:
            velocity = 0

    if not paused and velocity != 0:
        x += random.uniform(-3, 3)
        y += velocity


def draw():
    pyxel.cls(pyxel.COLOR_BLACK)

    if paused:
        pyxel.text(45, 60, "Clique para continuar!", pyxel.COLOR_WHITE)
    else:
        color = pyxel.COLOR_WHITE
        if velocity == 0:
            color = pyxel.COLOR_RED
        pyxel.circ(x, y, radius, color)

        if velocity == 0:
            pyxel.text(70, 90, "Parabens!", pyxel.COLOR_WHITE)


pyxel.init(180, 120)
pyxel.mouse(True)
pyxel.run(update, draw)
