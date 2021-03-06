import pyxel
from random import uniform, choice
from pymunk import Space, Body, Circle, Segment, Vec2d


def make_ball(x, y, vx, vy):
    body = Body(mass=1, moment=1)
    circle = Circle(body, 5)
    circle.elasticity = 1.0
    body.position = (x, y)
    body.velocity = (vx, vy)
    return body, circle 


class Game:
    """
    Jogo simples com a simulação de um círculo limitado à área visível da tela.
    """

    border_color = pyxel.COLOR_RED

    def __init__(self, fps=30, width=256, height=196, speed=50):
        x = lambda: uniform(5, width - 5)
        y = lambda: uniform(5, height - 5)
        v = lambda: choice([-speed, speed])

        self.fps = fps
        self.width = width
        self.height = height

        self.space = Space()
        self.space.gravity = (0, 50)

        # Cria círculos
        for _ in range(10):
            self.space.add(*make_ball(x(), y(), v(), v()))

        # Cria bordas
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

    def update(self):
        dt = 1 / self.fps
        self.space.step(dt)
        
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

    def run(self):
        pyxel.init(self.width, self.height, caption="Simulação de física", fps=self.fps)
        pyxel.mouse(True)
        pyxel.run(self.update, self.draw)



game = Game()
game.run()