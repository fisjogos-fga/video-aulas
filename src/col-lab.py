import pyxel
from functools import singledispatch
from pymunk import (
    Space,
    Body,
    Circle,
    Poly,
    Segment,
    Arbiter,
    Shape,
    ShapeFilter,
    Vec2d,
)
from pyxel.ui.number_picker import NumberPicker
from pyxel.ui.widget import Widget

MOMENT_FACTOR = 1000


class Game:
    """
    Jogo simples com a simulação de um círculo limitado à área visível da tela.
    """

    border_color = pyxel.COLOR_RED

    def __init__(self, fps=30, width=256, height=196, speed=50):
        self.fps = fps
        self.width = width
        self.height = height
        self.paused = True
        self.focus = None

        self.space = Space()
        self.space.gravity = (0, 0)
        self.focus = None

        # Widgets
        self.ui = Widget(None, 0, 0, 50, 100)
        self.elasticity = NumberPicker(self.ui, 12, 0, 0, 100, 100)
        self.friction = NumberPicker(self.ui, 12, 10, 0, 100, 0)
        self.gravity = NumberPicker(self.ui, 12, 20, 0, 100, 0)
        self.mass = NumberPicker(self.ui, 12, 30, 1, 100, 0)
        self.moment = NumberPicker(self.ui, 12, 40, 1, 100, 100)

        self._create_objects()

    def _create_objects(self):
        self.focus = Body(10, float("inf"))
        self.focus.position = (50, 100)
        self.focus.velocity = (150, 0)
        circle = Circle(self.focus, 15)
        circle.elasticity = 1
        self.space.add(self.focus, circle)

        positions = [(200, 100), (200, 50), (200, 150)]
        for pos in positions:
            b = Body(10, float("inf"))
            b.position = pos
            poly = Poly(b, [(-15, -20), (+15, -20), (+15, +20), (-15, +20)])
            poly.elasticity = 1
            self.space.add(b, poly)

        w, h = self.width, self.height
        self.borders = [
            Segment(self.space.static_body, (0, h), (w, h), 1),
            Segment(self.space.static_body, (0, 0), (w, 0), 1),
            Segment(self.space.static_body, (0, 0), (0, h), 1),
            Segment(self.space.static_body, (w, 0), (w, h), 1),
        ]
        for shape in self.borders:
            shape.elasticity = 1.0
        self.space.add(*self.borders)

        self.space.step(0.001)
        self.mass.value = self.focus.mass

    def update(self):
        self.update_widgets()
        self.update_focus()

        if pyxel.btnp(pyxel.KEY_SPACE):
            self.paused = not self.paused

        if pyxel.btnp(pyxel.KEY_S):
            self.paused = True

        if not self.paused or pyxel.btnp(pyxel.KEY_S):
            dt = 1 / self.fps
            self.space.step(dt)

    def update_widgets(self):
        self.ui.update_widgets()

        for shape in self.space.shapes:
            shape.elasticity = self.elasticity.value / 100
            shape.friction = self.friction.value / 100
        self.space.gravity = (0, self.gravity.value)

        self.focus.mass = self.mass.value
        if self.moment.value == 100:
            self.focus.moment = float("inf")
        else:
            self.focus.moment = self.moment.value * MOMENT_FACTOR

    def update_focus(self):
        mouse_pos = Vec2d(pyxel.mouse_x, pyxel.mouse_y)
        focus = self.focus

        for info in self.space.point_query(mouse_pos, 1, ShapeFilter()):
            if info.shape.body != self.space.static_body:
                self.focus = focus = info.shape.body
                self.mass.value = self.focus.mass
                self.moment.value = min(self.focus.moment / MOMENT_FACTOR, 100)
                break

        if pyxel.btnp(pyxel.KEY_UP):
            focus.velocity += (0, -10)
        if pyxel.btnp(pyxel.KEY_DOWN):
            focus.velocity += (0, +10)
        if pyxel.btnp(pyxel.KEY_LEFT):
            focus.velocity += (-10, 0)
        if pyxel.btnp(pyxel.KEY_RIGHT):
            focus.velocity += (10, 0)

    def draw(self):
        pyxel.cls(pyxel.COLOR_BLACK)

        # Desenha widgets
        self.ui.draw_widgets()
        pyxel.text(0, 0, "e:", pyxel.COLOR_WHITE)
        pyxel.text(0, 10, "mu:", pyxel.COLOR_WHITE)
        pyxel.text(0, 20, "g:", pyxel.COLOR_WHITE)
        pyxel.text(0, 30, "m:", pyxel.COLOR_WHITE)
        pyxel.text(0, 40, "I:", pyxel.COLOR_WHITE)
        pyxel.text(0, 50, "aperte <shift>", pyxel.COLOR_DARKBLUE)

        # Desenha elementos do espaço
        for shape in self.space.shapes:
            if isinstance(shape, Circle):
                circle: Circle = shape
                b: Body = circle.body
                r = circle.radius
                x, y = b.position
                pos = b.position + b.rotation_vector * shape.radius
                pyxel.circ(x, y, r, pyxel.COLOR_RED)
                pyxel.line(x, y, *pos, pyxel.COLOR_BLACK)
            elif isinstance(shape, Poly):
                fn = shape.body.local_to_world
                vs = [fn(u) for u in shape.get_vertices()]
                for (x1, y1), (x2, y2), (x3, y3) in triangulate(vs):
                    pyxel.tri(x1, y1, x2, y2, x3, y3, pyxel.COLOR_RED)

        # Desenha árbitros
        for arbiter in self.arbiters():
            self.draw_arbiter(arbiter)

        # Desenha detalhes do elemento em foco
        self.draw_object_detail(self.focus, (0, 14))

    def draw_object_detail(self, obj, shift=(0, 0)):
        x, y = obj.position + shift
        props = {"v": "velocity", "s": "shapes"}
        show(x, y, obj, props)

    def draw_arbiter(self, arb: Arbiter):
        pset = arb.contact_point_set
        x, y = pt = pset.points[0].point_a

        color = pyxel.COLOR_GREEN if arb.is_first_contact else pyxel.COLOR_RED

        for pc in pset.points:
            pyxel.circ(*pc.point_a, 3, color)
            pyxel.circ(*pc.point_b, 3, color)
        pyxel.line(*pt, *(pt + 500 * arb.normal), color)
        pyxel.line(*pt, *(pt - 500 * arb.normal), color)

        fields = {
            "mu": "friction",
            "e": "restitution",
            "dK": "total_ke",
            "J": "total_impulse",
        }
        show(x, y - 28, arb, fields, color)

    def arbiters(self):
        bodies = set()
        for b in self.space.bodies:
            iter_arbiters = []
            b.each_arbiter(iter_arbiters.append)
            for arb in iter_arbiters:
                arb: Arbiter
                bs = {s.body for s in arb.shapes}
                if bs.intersection(bodies):
                    continue
                yield arb
            bodies.add(b)

    def run(self):
        pyxel.init(self.width, self.height, caption="Simulação de física", fps=self.fps)
        pyxel.mouse(True)
        pyxel.run(self.update, self.draw)


def show(x, y, obj, fields, color=pyxel.COLOR_WHITE):
    if isinstance(fields, dict):
        n = max(map(len, fields.keys()))
        for label, f in fields.items():
            value = render(getattr(obj, f))
            x_ = x - 5 * (len(label) - n + 1)
            pyxel.text(x_, y, label + ": " + value, color)
            y += 7
    else:
        for f in fields:
            pyxel.text(x, y, render(getattr(obj, f)), color)
            y += 7


@singledispatch
def render(obj):
    return str(obj)


@render.register(Vec2d)
def _(v):
    return f"{render(v.x)},{render(v.y)}"


@render.register(float)
def _(x):
    return f"{x:.0f}"


@render.register(list)
@render.register(set)
@render.register(tuple)
def _(xs):
    return ",".join(map(render, xs))


@render.register(Shape)
def _(s):
    return type(s).__name__


def triangulate(vs):
    fst, a, *rest = vs
    for b in rest:
        yield fst, a, b
        a = b


game = Game()
game.run()