#
# Jogos de plataforma
#
import random
import pyxel
from easymunk import Vec2d, Arbiter, march_string
from easymunk import pyxel as phys

WIDTH, HEIGHT = 256, 196
SCENARIO = """
|
|
|
|
|                                              =
|                                              ==
|                     ===                      ===
|                                              ====
|            ===   ===             ===         =====
|                                  ===
|=====    ===                      ===
|X
|X
"""


class Game:
    # Tipos de colisão
    PLAYER_COL_TYPE = 1
    ENEMY_COL_TYPE = 2
    END_COL_TYPE = 3

    # Velocidades
    PLAYER_SPEED = 90
    JUMP_SPEED = 120

    # Cores
    COLOR_ENEMY = pyxel.COLOR_CYAN

    # Outras propriedades
    CAMERA_TOL = Vec2d(WIDTH / 2 - 64, HEIGHT / 2 - 48)
    N_ENEMIES = 20

    def __init__(self, scenario=SCENARIO):
        self.camera = phys.Camera(flip_y=True)
        self.space = phys.space(
            gravity=(0, -25),
            wireframe=True,
            camera=self.camera,
            elasticity=1.0,
        )

        # Cria jogador
        self.player = phys.circ(
            50,
            50,
            4,
            color=pyxel.COLOR_RED,
            elasticity=0.0,
            collision_type=self.PLAYER_COL_TYPE,
        )
        self.can_jump = False
        self.game_over = False
        self.has_won = False

        # Cria chão
        f = phys.rect(0, 0, 1000, 48, body_type="static")

        # Cria cenário
        for line in march_string(
            scenario, "=", scale=8.0, translate=Vec2d(0.0, 48), flip_y=True
        ):
            line = [Vec2d(2 * x, y) for (x, y) in line]
            phys.poly(line, body_type="static", color=pyxel.COLOR_PEACH)

        # Cria sensor para condição de vitória
        phys.rect(
            1000 - 16,
            48,
            16,
            16,
            collision_type=self.END_COL_TYPE,
            sensor=True,
            body_type="static",
        )

        # Cria margens
        phys.margin(0, 0, 1000, HEIGHT)

        # Cria inimigos
        r = 16
        for _ in range(self.N_ENEMIES):

            vx = random.uniform(-self.PLAYER_SPEED / 3, self.PLAYER_SPEED / 3)
            vy = random.uniform(0, self.PLAYER_SPEED / 3)
            phys.circ(
                x=random.uniform(r, 1000 - r),
                y=random.uniform(HEIGHT / 2, HEIGHT - r),
                r=r,
                friction=0.0,
                angular_velocity=random.uniform(-10000, 10000),
                velocity=(vx, vy),
                color=self.COLOR_ENEMY,
                collision_type=self.ENEMY_COL_TYPE,
            )

        # Registra eventos de colisão
        self.register_collision_events()

    def register_collision_events(self):
        space = self.space

        @space.post_solve_collision(self.PLAYER_COL_TYPE, ...)
        def _(arb: Arbiter):
            n = arb.normal_from(self.player)
            self.can_jump = n.y <= -0.5

        @space.separate_collision(self.PLAYER_COL_TYPE, ...)
        def _(arb: Arbiter):
            self.can_jump = False

        @space.post_solve_collision(self.PLAYER_COL_TYPE, self.ENEMY_COL_TYPE)
        def _(arb: Arbiter):
            n = arb.normal_from(self.player)
            if n.y < 0.25:
                enemy = arb.other(self.player)
                space.remove(enemy.shape)
                space.remove(enemy)
            else:
                self.game_over = True 
                self.player.friction = 1.0

        @space.begin_collision(self.PLAYER_COL_TYPE, self.END_COL_TYPE)
        def _(arb: Arbiter):
            self.has_won = True
            return False

    def draw(self):
        pyxel.cls(pyxel.COLOR_BLACK)
        self.space.draw()

        msg = ""
        if self.game_over:
            msg = "GAME OVER"
        elif self.has_won:
            msg = "PARABENS!"

        if msg:
            x = (WIDTH - len(msg) * pyxel.FONT_WIDTH) / 2
            pyxel.text(x, HEIGHT / 2, msg, pyxel.COLOR_YELLOW)

    def update(self):
        self.space.step(1 / 30, 2)
        self.update_player()
        self.camera.follow(self.player.position, tol=self.CAMERA_TOL)

    def update_player(self):
        player = self.player
        v = player.velocity
        mass = player.mass
        F = mass * 200
        player.force += Vec2d(0, -mass * 200)

        if self.game_over:
            return

        if pyxel.btn(pyxel.KEY_LEFT):
            if self.can_jump:
                v = Vec2d(-self.PLAYER_SPEED, v.y)
            elif v.x <= 0:
                v = Vec2d(-self.PLAYER_SPEED / 2 / 2, v.y)
        elif pyxel.btn(pyxel.KEY_RIGHT):
            if self.can_jump:
                v = Vec2d(+self.PLAYER_SPEED, v.y)
            elif v.x <= 0:
                v = Vec2d(+self.PLAYER_SPEED / 2, v.y)
        else:
            r = 0.5 if self.can_jump else 1.0
            v = Vec2d(v.x * r, v.y)

        if self.can_jump and pyxel.btnp(pyxel.KEY_UP):
            v = Vec2d(v.x, self.JUMP_SPEED)

        player.velocity = v


pyxel.init(WIDTH, HEIGHT)
pyxel.mouse(True)
game = Game()
pyxel.run(game.update, game.draw)