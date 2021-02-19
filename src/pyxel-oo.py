import pyxel
from math import sqrt
import random

pyxel_has_init = False


class Ball:
    def __init__(self, x=90, y=None, radius=5, velocity=None):
        self.x = x
        self.radius = radius

        if y is None:
            y = random.uniform(0, 20)
        self.y = y

        if velocity is None:
            velocity = random.uniform(0.5, 1.5)
        self.velocity = velocity

    def click(self, x, y):
        dx = x - self.x
        dy = y - self.y
        if sqrt(dx ** 2 + dy ** 2) < self.radius:
            self.velocity = 0

    def draw(self):
        color = pyxel.COLOR_WHITE
        if self.velocity == 0:
            color = pyxel.COLOR_RED
        pyxel.circ(self.x, self.y, self.radius, color)

    def update(self):
        self.y += self.velocity


class Game:
    def __init__(self, width, height):
        global pyxel_has_init

        self.width = width
        self.height = height
        
        if not pyxel_has_init:
            pyxel.init(self.width, self.height)
            pyxel_has_init = True
            
    def update(self):
        ...

    def draw(self):
        ...

    def run(self):
        pyxel.run(self.update, self.draw)


class BallGame(Game):
    def __init__(self, width, height):
        super().__init__(width, height)
        self.balls = [Ball(10 + i) for i in range(0, 170, 25)]
        pyxel.mouse(True)

    def game_over(self) -> bool:
        return any(ball.y > self.height + ball.radius for ball in self.balls)

    def update(self):
        for ball in self.balls:
            if pyxel.btnp(pyxel.MOUSE_LEFT_BUTTON):
                ball.click(pyxel.mouse_x, pyxel.mouse_y)
            ball.update()

        if self.game_over():
            return GameOver(self.width, self.height)

    def draw(self):
        pyxel.cls(pyxel.COLOR_BLACK)

        for ball in self.balls:
            ball.draw()

        if all(ball.velocity == 0 for ball in self.balls):
            pyxel.text(70, 90, "Parabens!", pyxel.COLOR_WHITE)


class MenuGame(Game):
    def __init__(self, width, height):
        super().__init__(width, height)
        pyxel.mouse(True)

    def update(self):
        if pyxel.btnp(pyxel.MOUSE_LEFT_BUTTON):
            return BallGame(self.width, self.height)

    def draw(self):
        pyxel.cls(pyxel.COLOR_BLACK)
        pyxel.text(40, 60, "Clique para continuar", pyxel.COLOR_WHITE)


class GameState(Game):
    def __init__(self, game):
        self.game = game
    
    def update(self):
        response = self.game.update()
        if response is not None:
            self.game = response

    def draw(self):
        self.game.draw()


class GameOver(Game):
    def __init__(self, width, height):
        super().__init__(width, height)
        self.frames = iter(self.draw_frames())

    def draw_frames(self):
        ys = iter(self.text_ys())
        
        for _ in range(60):
            y = next(ys)
            
            pyxel.cls(pyxel.COLOR_BLACK)
            pyxel.text(51, y + 1, "GAME OVER!", (pyxel.frame_count // 3) % 16)
            pyxel.text(50, y, "GAME OVER!", pyxel.COLOR_WHITE)
            yield

        while True:
            pyxel.cls(pyxel.COLOR_BLACK)
            pyxel.text(51, 60, "Clique para continuar!", pyxel.COLOR_WHITE)
            yield

    def text_ys(self):
        y = 0
        for y in range(y, 65, 4):
            yield y
        
        for _ in range(2):
            yield y
        
        for _ in range(2):
            y += 1
            yield y
        y -= 4
        
        while True:
            yield y

    def draw(self):
        next(self.frames)
        


#game = GameState(MenuGame(180, 120))
game = GameOver(180, 120)
game.run()
