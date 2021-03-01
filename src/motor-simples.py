import pyxel
from math import sqrt
from random import uniform, choice


class Space:
    def __init__(self):
        self.objects = []

    def add(self, obj):
        self.objects.append(obj)
        obj.space = self

    def update(self, dt):
        for obj in self.objects:
            obj.update_velocities(dt)
        
        for i, obj_a in enumerate(self.objects):
            for obj_b in self.objects[i + 1:]:
                if obj_a.collides_with(obj_b):
                    self.resolve_collision_pair(obj_a, obj_b)

        for obj in self.objects:
            self.resolve_wall_collisions(obj)
        
        for obj in self.objects:
            obj.update_positions(dt)

    def draw(self):
        for obj in self.objects:
            obj.draw()

    def resolve_collision_pair(self, obj_a, obj_b):
        x = obj_b.x - obj_a.x
        y = obj_b.y - obj_a.y
        r = sqrt(x**2 + y**2)

        vx = obj_b.vx - obj_a.vx
        vy = obj_b.vy - obj_a.vy

        vrel = (x/r * vx + y/r * vy)
        obj_a.vx += vrel * (x / r)
        obj_a.vy += vrel * (y / r)
        obj_b.vx -= vrel * (x / r)
        obj_b.vy -= vrel * (y / r)

    def resolve_wall_collisions(self, obj):
        if obj.x < obj.radius - 1 and obj.vx < 0:
            obj.vx *= -1
        elif obj.x > pyxel.width - obj.radius - 1 and obj.vx > 0:
            obj.vx *= -1
        if obj.y < obj.radius - 1 and obj.vy < 0:
            obj.vy *= -1
        elif obj.y > pyxel.height - obj.radius - 1 and obj.vy > 0:
            obj.vy *= -1

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
        for _ in range(10):
            ball = Ball(x(), y(), v(), v())
            self.space.add(ball)

    def update(self):
        n = 10
        dt = 1 / self.fps / n
        for _ in range(n):
            self.space.update(dt)

    def draw(self):
        pyxel.cls(pyxel.COLOR_BLACK)

        # Bordas
        w, h = self.width, self.height
        pyxel.line(0, 0, w, 0, self.border_color)
        pyxel.line(w - 1, 0, w - 1, h - 1, self.border_color)
        pyxel.line(w - 1, h - 1, 0, h - 1, self.border_color)
        pyxel.line(0, h - 1, 0, 0, self.border_color)

        self.space.draw()

    def run(self):
        pyxel.init(self.width, self.height, caption="Simulação de física", fps=self.fps)
        pyxel.mouse(True)
        pyxel.run(self.update, self.draw)


class Ball:
    """
    Bola com colisões com as paredes do mundo.
    """

    color = pyxel.COLOR_WHITE

    def __init__(self, x, y, vx=0, vy=0, radius=5, mass=1):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.fx = 0
        self.fy = 50
        self.mass = mass
        self.radius = radius
        self.space = None

    def update_velocities(self, dt):
        # Segunda lei de Newton: F = m a = dp / dt; p = m v
        ax = self.fx / self.mass
        ay = self.fy / self.mass

        # a = dv / dt ~= (v' - v) / dt
        # v' = v + a * dt
        self.vx = self.vx + ax * dt
        self.vy = self.vy + ay * dt

    def update_positions(self, dt):
        # v = dx / dt ~= (x' - x) / dt
        # x' - x = v * dt
        # x' = x + v * dt
        self.x = self.x + self.vx * dt
        self.y = self.y + self.vy * dt

    def collides_with(self, other) -> bool:
        x, y = self.x, self.y
        x_, y_ = other.x, other.y
        distance = sqrt((x - x_)**2 + (y - y_)**2)
        return distance <= self.radius + other.radius

    def draw(self):
        pyxel.circ(self.x, self.y, self.radius, self.color)


game = Game()
game.run()
