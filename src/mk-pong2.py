import pyxel
import random
from easymunk import Vec2d
from easymunk import pyxel as phys

FPS = 30
SPEED = 50
VELOCITIES = [Vec2d(x, y) for x in [-SPEED, SPEED] for y in [-SPEED, SPEED]]
SCREEN = Vec2d(180, 120)


class Game:
    SPEED = 60
    SHAPE = Vec2d(4, 16)

    def __init__(self):
        self.paused = True
        self.space = phys.space()
        phys.margin(-50, 0, width=SCREEN.x + 100, elasticity=1.0)

        y = SCREEN.y / 2
        self.ball = phys.circ(0, 0, 3, density=1.0, elasticity=1.0)
        self.p1 = phys.rect(5, y, *self.SHAPE, body_type="kinematic", elasticity=1.0)
        self.p2 = phys.rect(SCREEN.x - 5, y, *self.SHAPE, body_type="kinematic", elasticity=1.0)

        self.restart()

    def restart(self):
        w, h = SCREEN
        y = h / 2 - self.SHAPE.y / 2
        self.ball.apply(position=SCREEN / 2, velocity=(0, 0))
        self.p1.apply(position=(5, y), velocity=(0, 0))
        self.p2.apply(position=(w - 5, y), velocity=(0, 0))

    def update(self):
        if self.paused and pyxel.btnp(pyxel.KEY_SPACE):
            self.ball.velocity = random.choice(VELOCITIES)
            self.paused = False
        self.update_player(self.p1, pyxel.KEY_W, pyxel.KEY_S)
        self.update_player(self.p2, pyxel.KEY_UP, pyxel.KEY_DOWN)
        self.space.step(1 / 30)

    def update_player(self, body, key_up, key_down):
        if pyxel.btn(key_up):
            body.velocity = Vec2d(0, -self.SPEED)
        elif pyxel.btn(key_down):
            body.velocity = Vec2d(0, self.SPEED)
        else:
            body.velocity = Vec2d(0, 0)

    def draw(self):
        pyxel.cls(pyxel.COLOR_BLACK)
        self.space.draw()

    def run(self):
        pyxel.run(self.update, self.draw)


pyxel.init(*SCREEN, caption="PONG")
pyxel.mouse(True)
game = Game()
game.run()
