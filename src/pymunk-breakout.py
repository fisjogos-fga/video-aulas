import pyxel
import random
from pymunk import Space, Body, Circle, Poly, Segment, BB, Arbiter, Vec2d

FPS = 30
WIDTH, HEIGHT = SCREEN = (256, 196)


class Game:
    PLAYER_SHAPE = (25, 6)
    BLOCK_SHAPE = PLAYER_SHAPE
    PLAYER_SPEED = 90
    BALL_SPEED = 60
    BALL_COL_TYPE = 1
    BLOCK_COL_TYPE = 2
    DIV_LINE_COL_TYPE = 3

    def __init__(self):
        self.paused = True
        self.space = Space()

        # Cria jogadores
        x, y = WIDTH / 2, HEIGHT - 5
        self.player = Body(body_type=Body.KINEMATIC)
        self.player.position = (x, y)

        shape = Poly.create_box(self.player, self.PLAYER_SHAPE)
        shape.elasticity = 1.0
        self.space.add(self.player, shape)

        # Cria bola
        self.ball = Body(1, 1)
        shape = Circle(self.ball, 3)
        shape.elasticity = 1.0
        shape.collision_type = self.BALL_COL_TYPE
        self.space.add(self.ball, shape)

        # Cria bordas
        w, h = WIDTH, HEIGHT
        top = Segment(self.space.static_body, (0, 0), (w, 0), 5)
        left = Segment(self.space.static_body, (0, 0), (0, h), 5)
        right = Segment(self.space.static_body, (w, 0), (w, h), 5)
        top.elasticity = left.elasticity = right.elasticity = 1.0
        self.space.add(top, left, right)

        # Cria blocos
        x0, y0 = 20, 15
        w, h = self.BLOCK_SHAPE
        for dx in range(0, WIDTH - 25, w + 1):
            for dy in range(0, HEIGHT // 3, h + 1):
                self.make_block(x0 + dx, y0 + dy)

        # Cria linha divisória
        y = HEIGHT // 2 + 4 * self.BLOCK_SHAPE[1]
        a, b = (0, y), (WIDTH, y)
        shape = Segment(self.space.static_body, a, b, 3)
        shape.elasticity = 1.0
        shape.collision_type = self.DIV_LINE_COL_TYPE
        # self.space.add(shape)

        # Registra função para atuar nos eventos de colisão
        handler = self.space.add_collision_handler(self.BLOCK_COL_TYPE, self.BALL_COL_TYPE)
        handler.separate = self.on_collision
 
        handler = self.space.add_collision_handler(self.DIV_LINE_COL_TYPE, self.BALL_COL_TYPE)
        handler.begin = self.on_div_line_collision

    def on_collision(self, arb: Arbiter, space, data):
        for shape in arb.shapes:
            if shape.collision_type == self.BLOCK_COL_TYPE:
                space.remove(shape, shape.body)
        return True

    def on_div_line_collision(self, arb, space, data):
        return False

    def make_block(self, x, y):
        body = Body(2, float('inf'), body_type=Body.STATIC)
        body.position = (x, y)

        shape = Poly.create_box(body, self.BLOCK_SHAPE)
        shape.elasticity = 1.0
        shape.collision_type = self.BLOCK_COL_TYPE
        self.space.add(body, shape)

    def update(self):
        # Atualiza a velocidade
        sign = lambda x: -1 if x < 0 else 1

        F = 100
        F *= sign(self.PLAYER_SPEED - self.ball.velocity.length)
        self.ball.force += F * self.ball.velocity.normalized()

        v: Vec2d = self.ball.velocity
        i = round((v.angle_degrees - 45) * 4 / 360)
        angle = 45 + i * 360 / 4 
        self.ball.force += (angle - v.angle_degrees) * self.ball.velocity.normalized().rotated_degrees(90)
        
        dt = 1 / FPS
        self.space.step(dt)

        # Inicia o jogo quando aperta espaço
        if self.paused and pyxel.btnp(pyxel.KEY_SPACE):
            speed = self.BALL_SPEED
            vx = random.choice([-speed, +speed])
            self.ball.velocity = (vx, - 1.5 * speed)
            self.paused = False

        # Atualizar o estado da plataforma
        if pyxel.btn(pyxel.KEY_LEFT):
            self.player.velocity = (-self.PLAYER_SPEED, 0)
        elif pyxel.btn(pyxel.KEY_RIGHT):
            self.player.velocity = (self.PLAYER_SPEED, 0)
        else:
            self.player.velocity = (0, 0)

        # Carrega a bola quando o jogo estiver pausado
        if self.paused:
            self.ball.position = self.player.position + (0, -6)

    def draw(self):
        pyxel.cls(pyxel.COLOR_BLACK)

        for shape in self.space.shapes:
            if isinstance(shape, Circle):
                x, y = shape.body.position + shape.offset
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
