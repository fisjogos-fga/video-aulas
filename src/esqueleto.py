from easymunk import pyxel as phys, Vec2d, ShapeFilter
import pyxel

pyxel.init(256, 196)
pyxel.mouse(True)
space = phys.space(
    camera=phys.Camera(flip_y=True),
    sub_steps=3,
    friction=0.5,
    damping=0.95,
    gravity=Vec2d(0, -500),
)


@space.before_step()
def _():
    if pyxel.btnp(pyxel.KEY_SPACE):
        if pin.stiffness == 0.0:
            pin.stiffness = 1e5
        else:
            pin.stiffness = 0.0


# Cria elementos
x, y = 128, 150
shape_filter = ShapeFilter(group=1)
head = phys.circ(x, y + 5, 10, filter=shape_filter)
body = phys.line(x, y - 15, x, y - 70, radius=8, filter=shape_filter)
arm_1 = phys.line(x - 7, y - 15, x - 70, y - 15, radius=4, filter=shape_filter)
arm_2 = phys.line(x + 7, y - 15, x + 70, y - 15, radius=4, filter=shape_filter)
leg_1 = phys.line(x - 9, y - 73, x - 10, y - 140, radius=5, filter=shape_filter)
leg_2 = phys.line(x + 9, y - 73, x + 10, y - 140, radius=5, filter=shape_filter)
floor = phys.rect(0, 0, 256, 8, body_type="static")
phys.margin()

# Cria junções
pin = body.spring_to((25, 80), 1e5, rest_length=50)
head.junction(body).pivot((0, -20))
arm_1.junction(body).pivot(arm_1.a)
arm_2.junction(body).pivot(arm_2.a)
leg_1.junction(body).pivot(leg_1.a)
leg_2.junction(body).pivot(leg_2.a)

# Limita junções
head.junction(body).fix_angle(-30, 30)
arm_1.junction(body).fix_angle(-80, 60)
arm_2.junction(body).fix_angle(-60, 80)
leg_1.junction(body).fix_angle(-10, 80)
leg_2.junction(body).fix_angle(-80, 10)

# Limita junções
head.junction(body).rotary_spring(1e6, 5e4)
arm_1.junction(body).rotary_spring(1e5, 5e4)
arm_2.junction(body).rotary_spring(1e5, 5e4)
leg_1.junction(body).rotary_spring(1e6, 5e4)
leg_2.junction(body).rotary_spring(1e6, 5e4)

# Inicializa a simulação
space.run()