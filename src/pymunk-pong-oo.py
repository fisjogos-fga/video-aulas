import pyxel
import random
from pymunk import Space, Body, Circle, Poly, Segment, BB, Vec2d

FPS = 30
WIDTH, HEIGHT = SCREEN = Vec2d(180, 120)


class Game:
    PLAYER_SHAPE = (4, 16)
    PLAYER_SPEED = 30

    def __init__(self):
        self.paused = True
        self.space = Space()

        # Cria bola
        self.ball = Body()
        self.ball.position = SCREEN / 2
        shape = Circle(self.ball, 3)
        shape.density = 1.0
        shape.elasticity = 1.0
        self.space.add(self.ball, shape)

        # Cria jogadores
        y = HEIGHT / 2
        self.p1 = self.make_player(5, y, pyxel.KEY_W, pyxel.KEY_S)
        self.p2 = self.make_player(WIDTH - 5, y, pyxel.KEY_UP, pyxel.KEY_DOWN)

        # Cria bordas
        w, h = WIDTH, HEIGHT
        top = Segment(self.space.static_body, (0, 0), (w, 0), 1)
        bottom = Segment(self.space.static_body, (0, h), (w, h), 1)
        top.elasticity = bottom.elasticity = 1.0
        self.space.add(top, bottom)

    def make_player(self, x, y, key_up, key_down):
        """
        Cria jogador e associa teclas key_up e key_down.
        """
        body = Body(body_type=Body.KINEMATIC)
        body.position = (x, y)
        body.key_up = key_up
        body.key_down = key_down

        shape = Poly.create_box(body, self.PLAYER_SHAPE)
        shape.elasticity = 1.0

        self.space.add(body, shape)
        return body

    def update(self):
        dt = 1 / FPS
        self.space.step(dt)

        # Inicia o jogo quando aperta espaço
        if self.paused and pyxel.btnp(pyxel.KEY_SPACE):
            speed = 50
            vx = random.choice([-speed, +speed])
            vy = random.choice([-speed, +speed])
            self.ball.velocity = (vx, vy)
            self.paused = False

    def update_player(self, player):
        if pyxel.btn(player.key_up):
            player.velocity = (0, -self.PLAYER_SPEED)
        elif pyxel.btn(player.key_down):
            player.velocity = (0, self.PLAYER_SPEED)
        else:
            player.velocity = (0, 0)

    def draw(self):
        pyxel.cls(pyxel.COLOR_BLACK)

        for shape in self.space.shapes:
            if isinstance(shape, Circle):
                x, y = shape.body.position
                r = shape.radius
                pyxel.circ(x, y, r, pyxel.COLOR_RED)
            elif isinstance(shape, Poly):
                bb: BB = shape.bb
                x = bb.left
                y = bb.bottom
                width = bb.right - bb.left
                height = bb.top - bb.bottom
                pyxel.rect(x, y, width, height, pyxel.COLOR_WHITE)


game = Game()
pyxel.init(WIDTH, HEIGHT, fps=FPS)
pyxel.mouse(True)
pyxel.run(game.update, game.draw)
