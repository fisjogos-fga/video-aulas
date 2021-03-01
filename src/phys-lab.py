import pyxel
from math import cos
from collections import deque


class Game:
    """
    Jogo simples com a simulação de um círculo limitado à área visível da tela.
    """

    border_color = pyxel.COLOR_RED

    def __init__(self, fps=30, width=256, height=196, speed=50):
        self.fps = fps
        self.width = width
        self.height = height
        self.ball = Ball(50, 50, speed, -speed)
        self.positions = deque([(self.ball.x, self.ball.y)], maxlen=1024)

    def update(self):
        n = 10
        dt = 1 / self.fps / n
        for _ in range(n):
            self.ball.update(dt)
        self.positions.append((self.ball.x, self.ball.y))

    def draw(self):
        pyxel.cls(pyxel.COLOR_BLACK)

        # Bordas
        w, h = self.width, self.height
        pyxel.line(0, 0, w, 0, self.border_color)
        pyxel.line(w - 1, 0, w - 1, h - 1, self.border_color)
        pyxel.line(w - 1, h - 1, 0, h - 1, self.border_color)
        pyxel.line(0, h - 1, 0, 0, self.border_color)

        for x, y in self.positions:
            pyxel.pset(x, y, pyxel.COLOR_DARKBLUE)
        self.ball.draw()

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
        self.mass = mass
        self.radius = radius
        self.time = 0

    def update(self, dt):
        self.resolve_collisions()

        # Segunda lei de Newton: F = m a = dp / dt; p = m v
        fx, fy = self.force()
        ax = fx / self.mass
        ay = fy / self.mass

        # a = dv / dt ~= (v' - v) / dt
        # v' = v + a * dt
        self.vx = self.vx + ax * dt
        self.vy = self.vy + ay * dt

        # v = dx / dt ~= (x' - x) / dt
        # x' - x = v * dt 
        # x' = x + v * dt 
        self.x = self.x + self.vx * dt
        self.y = self.y + self.vy * dt

        self.time += dt

    def force(self):
        fx = 0
        fy = 0
        
        # Lei de Hooke
        k = 0.5
        x0 = 128
        y0 = 96
        fx += -k * (self.x - x0)
        fy += -k * (self.y - y0)
        
        # Disipassão viscosa
        gamma = 0.1
        fx += -gamma * self.vx
        fy += -gamma * self.vy

        return fx, fy

    def resolve_collisions(self):
        if self.x < self.radius - 1 and self.vx < 0:
            self.vx *= -1
        elif self.x > pyxel.width - self.radius - 1 and self.vx > 0:
            self.vx *= -1
        if self.y < self.radius - 1 and self.vy < 0:
            self.vy *= -1
        elif self.y > pyxel.height - self.radius - 1 and self.vy > 0:
            self.vy *= -1

    def draw(self):
        pyxel.circ(self.x, self.y, self.radius, self.color)


game = Game()
game.run()
