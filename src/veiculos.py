#
# Veículos (visão lateral)
#
import random
import pyxel
from easymunk import pyxel as phys, Vec2d
from svg_path import mk_path

palette = pyxel.DEFAULT_PALETTE.copy()
palette[pyxel.COLOR_RED] = 0xAA0000
pyxel.init(256, 196, palette=palette)
pyxel.mouse(True)

# Cria objetos no espaço
L = 5000
space = phys.space(
    camera=phys.Camera(flip_y=True),
    gravity=(0, -300),
    friction=1,
    elasticity=0.9,
    damping=0.9,
    sub_steps=4,
    bg=pyxel.COLOR_CYAN,
)
r = 100
phys.margin(-L, 0, 2 * L, 500, elasticity=0, radius=r, color=pyxel.COLOR_BROWN)

# Obstáculos aleatórios
for _ in range(150):
    x = random.uniform(-L + 100, L - 100)
    w = random.uniform(50, 100)
    w_ = random.uniform(50, 100)
    h = random.uniform(2, 10)
    phys.tri(x, r, x + w + w_, r, x + w, r + h, body_type="static", color=pyxel.COLOR_BROWN)


# Cria carro
p = "m 64,100 l 20,26 43,2 21,-21 -1,-3 -51,-17 -20,0 z"
vertices = [(x, 196 - y) for x, y in mk_path(p)]
body = phys.poly(vertices, pyxel.COLOR_RED, offset=(-10, -5 ))  #1
body.position -= (L / 2, 50 - r)
x, y = body.position
w1 = phys.circ(x - 45, y - 23, 15, pyxel.COLOR_BLACK, friction=1.5)
w2 = phys.circ(x + 40, y - 25, 13, pyxel.COLOR_BLACK, friction=1.5)

# Liga partes do carro por juntas
m1 = w1.motor(-3 * 360, max_force=0)

j1 = space.junction(body, w1)
j2 = space.junction(body, w2)

j1.fix_to_segment((-40, -10), (-45, -20), collide_bodies=False)
j2.fix_to_segment((+25, -10), (+30, -20), collide_bodies=False)

s1 = j1.spring(3e4, 1e4, anchor_a=(-35, -0))
s2 = j2.spring(2e4, 7e3, anchor_a=(+20, -0))
s1.rest_length *= 1.5
s2.rest_length *= 1.5


@space.before_step()
def f0():
    if pyxel.btn(pyxel.KEY_RIGHT):
        m1.max_force = 5e6
    else:
        m1.max_force = 0

    if pyxel.btnp(pyxel.KEY_SPACE):
        body.angular_velocity += 90


@space.after_step()
def f1():
    vx, vy = body.velocity
    space.camera.offset += (vx / 20, vy / 10 + 0.5)  
    space.camera.follow(body.position, tol=(64, 48))
    pyxel.text(0, 0, f'v: {int(body.velocity.x)}', pyxel.COLOR_BLACK)


space.run()

#1: o vídeo foi gravado com um bug na inicialização de polígonos, que escolhia 
#   um centro de gravidade incorreto. Por isso, foi necessário ajustar um 
#   "offset" para ajustar a posição do polígono para o comportamento anterior.