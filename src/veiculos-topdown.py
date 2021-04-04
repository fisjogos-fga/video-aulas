#
# Veículos (visão lateral)
#
from math import copysign
import pyxel
from easymunk import pyxel as phys, Vec2d

pyxel.init(256, 196)
pyxel.mouse(True)

# Cria objetos no espaço
space = phys.space(
    camera=phys.Camera(flip_y=True),
    friction=1.0,
    elasticity=1.0,
    damping=0.95,
    bg=pyxel.COLOR_GRAY,
)
phys.margin()


# Cria corpo do carro
c1 = pyxel.COLOR_DARKBLUE
c2 = pyxel.COLOR_NAVY
car = phys.poly([(-7, -6), (4, -4), (4, 4), (-7, 6)], color=c1, position=(128, 98))
car.create_poly([(12, -5), (14, -4), (14, 4), (12, 5)], color=c2, density=0.1)
car.create_poly([(-18, -5), (-15, -5), (-15, 5), (-18, 5)], color=c1, density=0.1)
car.create_poly([(-14, -4), (15, 0), (-14, 4)], color=c2)
car.create_circle(1, offset=(-4, 0), color=pyxel.COLOR_WHITE)

# Cria rodas
x, y = car.position
w1, w2, w3, w4 = wheels = [
    space.create_segment((x + 6, y - 5), (x + 9, y - 5), color=pyxel.COLOR_BLACK),
    space.create_segment((x + 6, y + 5), (x + 9, y + 5), color=pyxel.COLOR_BLACK),
    space.create_segment((x - 9, y - 6), (x - 13, y - 6), color=pyxel.COLOR_BLACK),
    space.create_segment((x - 9, y + 6), (x - 13, y + 6), color=pyxel.COLOR_BLACK),
]

# Cria juntas entre as rodas e o carro
w1.junction(car).pivot()
w2.junction(car).pivot()
w3.junction(car).pivot()
w4.junction(car).pivot()
r1 = w1.junction(car).fix_angle(max_bias=4)
r2 = w2.junction(car).fix_angle(max_bias=4)
w3.junction(car).fix_angle()
w4.junction(car).fix_angle()

mu = 0.5
vmax = 200
delta_vt = 50
mass = car.mass + w1.mass + w2.mass + w3.mass + w4.mass

@space.before_step()
def f1():
    dt = 1 / 30
    speed = car.velocity.length
    r = max(1 - speed / vmax, 0)

    angle, force = phys.arrow(25 + 20 * r, 100 * r * mass)
    r1.angle = r2.angle = angle
    
    w3.apply_force_at_local_point((force, 0))
    w4.apply_force_at_local_point((force, 0))

    for w in wheels:
        u = w.rotation_vector
        vel = w.velocity

        vt = u.cross(vel)

        Fat = mass * min(mu * 300, 0.25 * min(abs(vt), delta_vt) / dt)
        Fat = copysign(Fat, -vt)
        w.apply_force_at_local_point((0, Fat))
        


if space.draw_options is not None:
    space.draw_options.flags = space.draw_options.DRAW_SHAPES
space.run()
