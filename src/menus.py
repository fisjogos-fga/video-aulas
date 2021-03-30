import pyxel


class Button:
    def __init__(self, text, action, y, color=pyxel.COLOR_BLACK):
        self.text = text
        self.action = action
        self.color = color
        self.y = y
        self._y_margin = 3
        self._h = pyxel.FONT_HEIGHT + 2 * self._y_margin
        self._w = 100
        self._x0 = (pyxel.width - self._w) / 2
        self._x1 = self._x0 + self._w
        self._is_under_mouse = False
        self._send_message = None

    def draw(self):
        w = 100
        if self._is_under_mouse:
            col = pyxel.COLOR_CYAN
        else:
            col = pyxel.COLOR_LIGHTBLUE

        pyxel.rect(self._x0, self.y, w, self._h, col)
        centralized_text(self.y + self._y_margin, self.text, self.color)

    def update(self):
        x: int = pyxel.mouse_x
        y: int = pyxel.mouse_y

        if self.y <= y <= self.y + self._h and self._x0 <= x <= self._x1:
            self._is_under_mouse = True
        else:
            self._is_under_mouse = False

        if self._is_under_mouse and pyxel.btnp(pyxel.MOUSE_LEFT_BUTTON):
            if self._send_message is not None:
                msg = self._send_message
                msg(self.action, sender=self)

    def register(self, msg, **kwargs):
        self._send_message = msg

    def message(self, msg, *args, sender=None):
        ...


class Menu:
    """
    Implementa um menu de jogo

    SUPER PYTHON Bros.

    [Começar Jogo]
    [Ranking]
    [Ajuda]
    """

    def __init__(self, background=pyxel.COLOR_BLACK):
        self.name = "SUPER PYTHON BROS."
        self.background = background

        y0 = 60
        dy = 30
        self.buttons = [
            Button("Comecar Jogo", "start", y0),
            Button("Ranking", "rank", y0 + dy),
            Button("Ajuda", "help", y0 + dy * 2),
        ]
        for button in self.buttons:
            button.register(self.message)

    def draw(self):
        if self.background is not None:
            pyxel.cls(self.background)

        centralized_text(10, self.name, pyxel.COLOR_WHITE)
        for button in self.buttons:
            button.draw()

    def update(self):
        for button in self.buttons:
            button.update()

    def register(self, msg, **kwargs):
        ...

    def message(self, msg, *args, sender=None):
        function = getattr(self, f"handle_{msg}", None)
        if function is None:
            print('msg inválida: {msg}')
        else:
            function(*args, sender=sender)

    def handle_start(self, sender):
        print('start!')

    def handle_help(self, sender):
        print('help!')

    def handle_rank(self, sender):
        print('rank!')


def centralized_text(y, text, col):
    n = len(text)
    x = (pyxel.width - n * pyxel.FONT_WIDTH) / 2
    pyxel.text(x, y, text, col)



class Game:
    def __init__(self, background=pyxel.COLOR_BLACK):
        self.menu = ...
        self.help = ...
        self.ranking = ...
        self.running = ... 
        self.state = self.menu
        self.state_map = {
            "menu": self.menu,
            "help": self.help,
            "ranking": self.ranking,
            "running": self.running,
        }

    def draw(self):
        self.state.draw()

    def update(self):
        self.state.update()

    def register(self, msg, **kwargs):
        ...

    def message(self, msg, sender=None):
        self.state = self.state_map[msg]


pyxel.init(256, 196, caption="Super Python Bros.")
pyxel.mouse(True)
menu = Menu()
pyxel.run(menu.update, menu.draw)