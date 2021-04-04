#
# Jogos de plataforma
#
import random
from typing import Callable
from abc import ABC, abstractmethod
import enum
import pyxel
from easymunk import Vec2d, Arbiter, CircleBody, Space, march_string
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


class ColType(enum.IntEnum):
    PLAYER = 1
    ENEMY = 2
    TARGET = 3


class GameState(enum.IntEnum):
    RUNNING = 1
    GAME_OVER = 2
    HAS_WON = 3


class GameObject(ABC):
    @abstractmethod
    def update(self):
        ...
    
    @abstractmethod
    def draw(self):
        ...

    @abstractmethod
    def register(self, space: Space, message: Callable[[str, "GameObject"], None]):
        ...


class Player(GameObject, CircleBody):
    SPEED = 90
    JUMP_SPEED = 120
    COLOR = pyxel.COLOR_RED

    def __init__(self, x, y):
        super().__init__(
            radius=4,
            position=(x, y),
            elasticity=0.0,
            collision_type=ColType.PLAYER,
        )
        self.can_jump = False

    def update(self):
        v = self.velocity
        mass = self.mass
        F = mass * 200
        self.force += Vec2d(0, -mass * 200)

        if pyxel.btn(pyxel.KEY_LEFT):
            if self.can_jump:
                v = Vec2d(-self.SPEED, v.y)
            elif v.x <= 0:
                v = Vec2d(-self.SPEED / 2 / 2, v.y)
        elif pyxel.btn(pyxel.KEY_RIGHT):
            if self.can_jump:
                v = Vec2d(+self.SPEED, v.y)
            elif v.x <= 0:
                v = Vec2d(+self.SPEED / 2, v.y)
        else:
            r = 0.5 if self.can_jump else 1.0
            v = Vec2d(v.x * r, v.y)

        if self.can_jump and pyxel.btnp(pyxel.KEY_UP):
            v = Vec2d(v.x, self.JUMP_SPEED)

        self.velocity = v

    def draw(self, camera=pyxel):
        x, y, _right, _top = self.bb
        sign = 1 if self.velocity.x >= 0 else -1

        idx = int(self.position.x / 2) % 4
        u = 8 * idx
        camera.blt(x, y, 0, u, 0, sign * 8, 8, pyxel.COLOR_YELLOW)

    def register(self, space, message):
        space.add(self)

        @space.post_solve_collision(ColType.PLAYER, ...)
        def _col_start(arb: Arbiter):
            n = arb.normal_from(self)
            self.can_jump = n.y <= -0.5

        @space.separate_collision(ColType.PLAYER, ...)
        def _col_end(arb: Arbiter):
            self.can_jump = False

        @space.begin_collision(ColType.PLAYER, ColType.TARGET)
        def _game_end(arb: Arbiter):
            message("hit_target", sender=self)
            return False


class Enemy(GameObject, CircleBody):
    SPEED = 90
    RADIUS = 16
    COLOR = pyxel.COLOR_CYAN
    
    @staticmethod
    def random(xmin, xmax, ymin, ymax):
        vx = random.uniform(-Enemy.SPEED / 3, Enemy.SPEED / 3)
        vy = random.uniform(0, Enemy.SPEED / 3)
        return Enemy(
            x=random.uniform(xmin + Enemy.RADIUS, xmax - Enemy.RADIUS),
            y=random.uniform(ymin + Enemy.RADIUS, ymax - Enemy.RADIUS),
            velocity=(vx, vy),
            angular_velocity=random.uniform(-360, 360),
        )

    def __init__(self, x, y, **kwargs):
        super().__init__(
            radius=self.RADIUS,
            position=(x, y),
            friction=0.0,
            elasticity=1.0,
            color=self.COLOR,
            collision_type=ColType.ENEMY,
            **kwargs,
        )

    def update(self):
        ...

    def draw(self, camera=pyxel):
        x, y = self.position
        camera.circb(x, y, self.radius, self.COLOR)

    def register(self, space, message):
        space.add(self)

        @space.begin_collision(ColType.PLAYER, ColType.ENEMY)
        def begin(arb: Arbiter):
            shape_a, shape_b = arb.shapes
            if shape_a.collision_type == ColType.PLAYER:
                player, enemy = shape_a, shape_b
            else:
                player, enemy = shape_b, shape_b

            n = arb.normal_from(player)
            if n.y < 0.25:
                space.remove(enemy)
            else:
                message("hit_player", sender=self)

            return True
                

class Game:
    # Cores

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

        # Inicializa o jogo
        self.state = GameState.RUNNING
        pyxel.load("assets.pyxres")

        # Cria jogador
        self.player = Player(50, 50)
        self.player.register(self.space, self.message)

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
            collision_type=ColType.TARGET,
            sensor=True,
            body_type="static",
        )

        # Cria margens
        phys.margin(0, 0, 1000, HEIGHT)

        # Cria inimigos
        for _ in range(self.N_ENEMIES):
            enemy = Enemy.random(0, 1000, HEIGHT / 2, HEIGHT)
            enemy.register(self.space, self.message)

    def message(self, msg, sender):
        fn = getattr(self, f'handle_{msg}', None)
        if fn is None:
            print(f'Mensagem desconhecida: "{msg} ({sender})')
        else:
            fn(sender)

    def handle_hit_player(self, sender):
        self.state = GameState.GAME_OVER

    def handle_hit_target(self, sender):
        self.state = GameState.HAS_WON

    def draw(self):
        pyxel.cls(0)
        for body in self.space.bodies:
            if isinstance(body, (Player, Enemy)):
                body.draw(self.camera)
            else:
                self.camera.draw(body)

        msg = ""
        if self.state is GameState.GAME_OVER:
            msg = "GAME OVER"
        elif self.state is GameState.HAS_WON:
            msg = "PARABENS!"

        if msg:
            x = (WIDTH - len(msg) * pyxel.FONT_WIDTH) / 2
            pyxel.text(round(x), HEIGHT // 2, msg, pyxel.COLOR_YELLOW)

    def update(self):
        self.space.step(1 / 30, 2)
        if self.state is not GameState.GAME_OVER:
            self.player.update()
        self.camera.follow(self.player.position, tol=self.CAMERA_TOL)


pyxel.init(WIDTH, HEIGHT)
pyxel.mouse(True)
game = Game()
pyxel.run(game.update, game.draw)