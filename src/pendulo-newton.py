import pyxel
from pymunk import Space, Body, Circle, Vec2d, ShapeFilter
from pymunk import PivotJoint, PinJoint
from code import InteractiveConsole
from threading import Thread


def make_ball(x, y, ground):
    body = Body(mass=1, moment=1)
    circle = Circle(body, 5)
    circle.elasticity = 0.95
    body.position = (x, y)
    
    anchor_a = (0, 0)
    anchor_b = ground.world_to_local(body.position + Vec2d(0, -90))
    pivot = PinJoint(body, ground, anchor_a, anchor_b)
    return body, circle, pivot 


def make_shell():
    shell = InteractiveConsole(globals())
    shell.interact()


class Game:
    """
    Jogo simples com a simulação de um círculo limitado à área visível da tela.
    """

    border_color = pyxel.COLOR_RED

    def __init__(self, fps=30, width=256, height=196, speed=50):
        self.fps = fps
        self.width = width
        self.height = height
        self.paused = False

        self.space = Space()
        self.space.gravity = (0, 100)

        # Cria círculos
        ground = self.space.static_body
        for i in range(10):
            self.space.add(*make_ball(136/2 + i * 12, 98, ground))


    def update(self):
        if not self.paused:
            dt = 1 / self.fps
            self.space.step(dt)

        if pyxel.btnp(pyxel.MOUSE_LEFT_BUTTON):
            pos = pyxel.mouse_x, pyxel.mouse_y
            lst = self.space.point_query(pos, 3, ShapeFilter())
            lst.sort(key=lambda i: i.distance)
            if lst:
                info = lst[0]
                if pyxel.btn(pyxel.KEY_CONTROL):
                    info.shape.body.velocity = (0, -100)
                else:
                    info.shape.body.velocity = (100, 0)
        
    def draw(self):
        pyxel.cls(pyxel.COLOR_BLACK)

        # Bordas
        w, h = self.width, self.height
        pyxel.line(0, 0, w, 0, self.border_color)
        pyxel.line(w - 1, 0, w - 1, h - 1, self.border_color)
        pyxel.line(w - 1, h - 1, 0, h - 1, self.border_color)
        pyxel.line(0, h - 1, 0, 0, self.border_color)

        # Desenha elementos do espaço
        for shape in self.space.shapes:
            if isinstance(shape, Circle):
                circle: Circle = shape
                r = circle.radius
                x, y = circle.body.position
                pyxel.circ(x, y, r, pyxel.COLOR_WHITE)

        for constraint in self.space.constraints:
            if isinstance(constraint, PivotJoint):
                a = constraint.a
                b = constraint.b
                pt_a = a.local_to_world(constraint.anchor_a)
                pt_b = b.local_to_world(constraint.anchor_b)
                pyxel.circ(*pt_a, 2, pyxel.COLOR_YELLOW)
                pyxel.circ(*pt_b, 2, pyxel.COLOR_YELLOW)
            if isinstance(constraint, PinJoint):
                a = constraint.a
                b = constraint.b
                pt_a = a.local_to_world(constraint.anchor_a)
                pt_b = b.local_to_world(constraint.anchor_b)
                pyxel.circ(*pt_a, 2, pyxel.COLOR_YELLOW)
                pyxel.circ(*pt_b, 2, pyxel.COLOR_YELLOW)
                pyxel.line(*pt_a, *pt_b, pyxel.COLOR_YELLOW)


    def run(self):
        pyxel.init(self.width, self.height, caption="Simulação de física", fps=self.fps)
        pyxel.mouse(True)
        pyxel.run(self.update, self.draw)


game = Game()
# thread = Thread(target=make_shell)
# thread.start()
game.run()
