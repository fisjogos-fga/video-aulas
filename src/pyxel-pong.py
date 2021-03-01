import pyxel
import random

FPS = 30


class Body:
    color = pyxel.COLOR_WHITE
    ay = 50

    def __init__(self, x, y, vx=0, vy=0):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy

    def update(self):
        dt = 1 / FPS
        self.x = self.x + self.vx * dt
        self.y = self.y + self.vy * dt + self.ay / 2 * dt**2
        self.vx = self.vx
        self.vy = self.vy + self.ay * dt

    def draw(self):
        pyxel.pset(self.x, self.y, self.color)


class Ball(Body):
    speed = 2 * FPS  # [px/s]
    color = pyxel.COLOR_RED

    def __init__(self, x, y, vx=0, vy=0, radius=3):
        super().__init__(x, y, vx, vy)
        self.radius = radius
        self.paused = True

    def update(self):
        if self.paused and pyxel.btnp(pyxel.KEY_SPACE):
            speed = self.speed
            self.vx = random.choice([-speed, +speed])
            self.vy = random.choice([-speed, +speed])
            self.paused = False

        # Detecta colisão com as paredes
        if self.y - self.radius < 0 and self.vy < 0:
            self.vy *= -1
        if self.y + self.radius > pyxel.height and self.vy > 0:
            self.vy *= -1

        # Detecta colisão com as pás
        if self.vx > 0:  # player 2
            if (
                player2.top < self.y < player2.bottom
                and self.x + self.radius > player2.left
                and self.x - self.radius < player2.right
            ):
                self.vx *= -1

        if self.vx < 0:  # player 1
            if (
                player1.top < self.y < player1.bottom
                and self.x - self.radius < player1.right
                and self.x + self.radius > player1.left
            ):
                self.vx *= -1

        super().update()

    def draw(self):
        pyxel.circ(self.x, self.y, self.radius, self.color)


class Paddle(Body):
    width = 4
    height = 16
    speed = 1 * FPS

    @property
    def top(self):
        return self.y - self.height / 2

    @property
    def bottom(self):
        return self.y + self.height / 2

    @property
    def left(self):
        return self.x - self.width / 2

    @property
    def right(self):
        return self.x + self.width / 2

    def __init__(self, x, y, vx=0, vy=0, *, key_up, key_down):
        super().__init__(x, y, vx, vy)
        self.key_up = key_up
        self.key_down = key_down

    def update(self):
        if pyxel.btn(self.key_up):
            self.vy = -self.speed
        elif pyxel.btn(self.key_down):
            self.vy = +self.speed
        else:
            self.vy = 0

        super().update()

    def draw(self):
        x = self.left
        y = self.top
        pyxel.rect(x, y, self.width, self.height, self.color)


def update():
    for obj in objects:
        obj.update()


def draw():
    pyxel.cls(pyxel.COLOR_BLACK)

    for obj in objects:
        obj.draw()


player1 = Paddle(5, 60, key_up=pyxel.KEY_W, key_down=pyxel.KEY_S)
player2 = Paddle(175, 60, key_up=pyxel.KEY_UP, key_down=pyxel.KEY_DOWN)
objects = [Ball(90, 60), player1, player2]
pyxel.init(180, 120, fps=FPS)
pyxel.mouse(True)
pyxel.run(update, draw)
