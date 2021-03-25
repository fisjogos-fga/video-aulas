#
# MODELO SIR
#
from copy import copy
from types import SimpleNamespace
from collections import deque
import random
from easymunk import pyxel as phys, Arbiter, BB, ShapeFilter
import pyxel


# Parâmetros da simulação
N = 5000
SPEED = 10
PROB_INFECTION = 0.25
INFECTIOUS_PERIOD = 30 * 5
PROB_DEATH = 0.01
SIZE = 500

# Constantes
S, I, R, D = range(1, 5)
COLORS = [None, pyxel.COLOR_PEACH, pyxel.COLOR_RED, pyxel.COLOR_LIME, pyxel.COLOR_ORANGE]
STATS = deque([], 256)
STATS_STEPS = 16

# Inicializa espaço e elementos
pyxel.init(256, 256)
pyxel.mouse(True)

space = phys.space()
stats = SimpleNamespace(S=N - 1, I=1, R=0, D=0)
camera = phys.Camera(flip_y=True)
camera.follow((0, 0))

# Cria elementos
circles = []
for _ in range(N):
    x = random.uniform(-SIZE / 2, +SIZE / 2)
    y = random.uniform(-SIZE / 2, +SIZE / 2)
    vel = random.uniform(-SPEED, SPEED), random.uniform(-SPEED, SPEED)
    c = phys.circ(x, y, 2, velocity=vel, collision_type=S)
    circles.append(c)

# Infecta o paciente zero
c = circles[-1]
c.shape.collision_type = I
c.frames_to_recovery = INFECTIOUS_PERIOD  # (days_to_recovery, no vídeo)
c.position = (128, 128)

# Margens
phys.margin(-SIZE / 2, -SIZE / 2, SIZE, SIZE)
space.shapes.apply(elasticity=1.0)


# Infecta um suscetível em contato com um infeccioso
@space.separate_collision(S, I)
def on_infection(arb: Arbiter):
    s, i = arb.shapes
    if s.collision_type != S:
        s, i = i, s

    if random.random() < PROB_INFECTION:
        s.collision_type = I
        s.body.frames_to_recovery = INFECTIOUS_PERIOD
        stats.S -= 1
        stats.I += 1


def update():
    camera.offset += phys.arrow(1, 1)
    space.step(1 / 30)

    for c in circles:
        if c.collision_type == I:
            c.frames_to_recovery -= 1

            if c.frames_to_recovery <= 0:
                stats.I -= 1

                if random.random() < PROB_DEATH:
                    stats.D += 1
                    c.collision_type = D
                    c.body_type = "static"
                else:
                    stats.R += 1
                    c.collision_type = R

    if pyxel.frame_count % STATS_STEPS == 0:
        STATS.append(copy(stats))

def draw():
    pyxel.cls(0)
    x, y = camera.offset
    bb = BB(x, y, x + 256, y + 256)
    for c in space.bb_query(bb, ShapeFilter()):
        if c.is_circle:
            x, y = c.position
            color = COLORS[c.collision_type]
            camera.pset(x, y, color)

    height = pyxel.height
    s = height / N
    for x, stat in enumerate(STATS):
        pyxel.pset(x, height - s * stat.S, COLORS[S])
        pyxel.pset(x, height - s * stat.I, COLORS[I])
        pyxel.pset(x, height - s * stat.R, COLORS[R])
        pyxel.pset(x, height - s * stat.D, COLORS[D])

    col = pyxel.COLOR_WHITE
    pyxel.text(0, 0, f'S = {stats.S}', col)
    pyxel.text(0, 10, f'I = {stats.I}', col)
    pyxel.text(0, 20, f'R = {stats.R}', col)
    pyxel.text(0, 30, f'D = {stats.D}', col)
    

pyxel.run(update, draw)



