from pymunk.arbiter import Arbiter
from pymunk.vec2d import Vec2d
import pyxel
import random
from pymunk import Space, Body, Circle, Poly, Segment, Vec2d, BB

FPS = 30
WIDTH, HEIGHT = 256, 196
SCREEN = Vec2d(WIDTH, HEIGHT)


#
# MOON LANDER
#
class Game:
    PLAYER_SHAPE = [(0, -4), (-2, 2), (+2, 2)]
    BASE_SHAPE = (20, 4)
    PLAYER_SPEED = 90
    PLAYER_COLOR = pyxel.COLOR_PINK
    BASE_COLOR = pyxel.COLOR_ORANGE 
    GRAVITY = Vec2d(0, 25)
    THRUST = -3 * GRAVITY
    ANGULAR_VELOCITY = 5
    FLOOR_STEP = 30
    FLOOR_DY = 15
    FLOOR_N = 42
    PLAYER_COL_TYPE = 1
    BASE_COL_TYPE = 2
    FLOOR_COL_TYPE = 3
    MAX_IMPULSE = 30

    def __init__(self):
        self.space = Space()
        self.space.gravity = self.GRAVITY
        self.camera_pos = Vec2d(0, 0)
        self.landed = False
        self.victory = False

        # Cria jogador
        self.player = Body(1, 2, body_type=Body.DYNAMIC)
        self.player.position = SCREEN / 2

        shape = Poly(self.player, self.PLAYER_SHAPE)
        shape.friction = 1.0
        shape.collision_type = self.PLAYER_COL_TYPE
        self.space.add(self.player, shape)

        # Cria base
        dx = random.uniform(-WIDTH, WIDTH)
        self.base = Body(body_type=Body.STATIC)
        self.base.position = self.player.position + (dx, 0.45 * HEIGHT)

        shape = Poly.create_box(self.base, self.BASE_SHAPE)
        shape.friction = 1.0
        shape.collision_type = self.BASE_COL_TYPE
        self.space.add(self.base, shape)

        # Cria chão
        shape = list(self.base.shapes)[0]
        bb = shape.cache_bb()
        self.make_floor(bb.right, bb.bottom, self.FLOOR_STEP, self.FLOOR_DY)
        self.make_floor(bb.left, bb.bottom, -self.FLOOR_STEP, self.FLOOR_DY)

        # Escuta colisões entre base/chão e jogador
        handler = self.space.add_collision_handler(self.PLAYER_COL_TYPE, self.BASE_COL_TYPE)
        handler.post_solve = self.on_land

        handler = self.space.add_collision_handler(self.PLAYER_COL_TYPE, self.FLOOR_COL_TYPE)
        handler.begin = self.on_collision

    def on_collision(self, arb: Arbiter, space, data):
        self.landed = True
        self.victory = False
        return True

    def on_land(self, arb: Arbiter, space, data):
        if not self.landed:
            self.victory = arb.total_impulse.length < self.MAX_IMPULSE
        self.landed = True
        
    def make_floor(self, x, y, step, dy):
        body = self.space.static_body
        
        a = Vec2d(x, y)
        for _ in range(self.FLOOR_N):
            b = a + (step, random.uniform(-dy, dy))
            shape = Segment(body, a, b, 2)
            shape.collision_type = self.FLOOR_COL_TYPE
            self.space.add(shape)
            a = b

    def update(self):
        if not self.landed:
            if pyxel.btn(pyxel.KEY_LEFT):
                self.player.angular_velocity = -self.ANGULAR_VELOCITY
            elif pyxel.btn(pyxel.KEY_RIGHT):
                self.player.angular_velocity = +self.ANGULAR_VELOCITY
            else:
                self.player.angular_velocity = 0.0
            
            if pyxel.btn(pyxel.KEY_UP):
                self.player.force += self.THRUST.rotated(self.player.angle)

        dt = 1 / FPS
        self.space.step(dt)
        self.camera_pos = self.player.position - SCREEN / 2

    def draw(self):
        pyxel.cls(pyxel.COLOR_BLACK)
        shift = self.camera_pos

        # Desenha o jogador
        transform = self.player.local_to_world
        shape = list(self.player.shapes)[0]
        a, b, c = [transform(v) - shift for v in shape.get_vertices()]
        pyxel.tri(*a, *b, *c, self.PLAYER_COLOR)

        # Desenha a base
        bb: BB = list(self.base.shapes)[0].bb
        x, y = (bb.left, bb.bottom) - shift
        pyxel.rect(x, y, *self.BASE_SHAPE, self.BASE_COLOR)

        # Desenha projéteis
        for shape in self.space.shapes:
            if isinstance(shape, Circle):
                x, y = shape.body.position - shift
                r = shape.radius
                pyxel.circ(x, y, r, pyxel.COLOR_RED)
            if isinstance(shape, Segment):
                transform = lambda v: shape.body.local_to_world(v) - shift
                a, b = map(transform, (shape.a, shape.b))
                pyxel.line(*a, *b, pyxel.COLOR_WHITE)

        if self.landed:
            msg = "PARABENS!" if self.victory else "PERDEU :("
            x = WIDTH / 2 - len(msg) * pyxel.FONT_WIDTH / 2
            pyxel.text(x, HEIGHT // 2 - 20, msg, pyxel.COLOR_RED)


game = Game()
pyxel.init(WIDTH, HEIGHT, fps=FPS)
pyxel.mouse(True)
pyxel.run(game.update, game.draw)
