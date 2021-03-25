import pyxel
import random
from easymunk import Vec2d
from easymunk import pyxel as phys


#
# EASYMUNK
#
FPS = 30
WIDTH, HEIGHT = 180, 120
SCREEN = Vec2d(WIDTH, HEIGHT)


class Game:
    PLAYER_SHAPE = (4, 16)
    PLAYER_SPEED = 30

    def __init__(self):
        self.paused = True
        self.camera = phys.Camera(flip_y=True)
        self.space = phys.space()

        # Cria bola
        x, y = SCREEN / 2
        self.ball = phys.circ(x, y, 3, pyxel.COLOR_RED, density=1.0, elasticity=1.0)

        # Mapa de comandos (teclas) para bodies
        self.keymap = {}

        # Cria jogadores
        y = HEIGHT / 2
        self.p1 = self.make_player(5, y, pyxel.KEY_W, pyxel.KEY_S)
        self.p2 = self.make_player(WIDTH - 5, y, pyxel.KEY_UP, pyxel.KEY_DOWN)

        # Cria bordas
        w, h = SCREEN
        phys.margin(-50, 0, w + 100, h, elasticity=1.0)

    def make_player(self, x, y, key_up, key_down):
        """
        Cria jogador e associa teclas key_up e key_down.
        """
        w, h = self.PLAYER_SHAPE
        x, y = x - w / 2, y - h / 2
        body = phys.rect(x, y, w, h, elasticity=1.0, body_type="kinematic")
        self.keymap[body] = (key_up, key_down)
        return body

    def update(self):
        dt = 1 / FPS

        # Inicia o jogo quando aperta espaço
        if self.paused and pyxel.btnp(pyxel.KEY_SPACE):
            speed = 50
            vx = random.choice([-speed, +speed])
            vy = random.choice([-speed, +speed])
            self.ball.velocity = (vx, vy)
            self.paused = False

        self.update_player(self.p1)
        self.update_player(self.p2)
        self.space.step(dt)

    def update_player(self, player):
        key_up, key_down = self.keymap[player]
        if pyxel.btn(key_up):
            player.velocity = (0, +self.PLAYER_SPEED)
        elif pyxel.btn(key_down):
            player.velocity = (0, -self.PLAYER_SPEED)
        else:
            player.velocity = (0, 0)

    def draw(self):
        pyxel.cls(pyxel.COLOR_BLACK)
        self.camera.drawb(self.p1)
        self.camera.drawb(self.p2)
        self.camera.drawb(self.ball)

pyxel.init(WIDTH, HEIGHT, fps=FPS)
pyxel.mouse(True)
game = Game()
pyxel.run(game.update, game.draw)
