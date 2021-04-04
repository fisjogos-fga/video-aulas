import random
import pyxel
from easymunk import pyxel as phys, Vec2d
import easymunk as mk

pyxel.init(256, 196)
pyxel.mouse(True)

camera = phys.Camera(flip_y=True)
space = phys.space(camera=camera, gravity=(0, -200))
scale = Vec2d(48, 8)


a, b = Vec2d(0, 0), Vec2d(500, 0)
space.static_body.create_segment(a, b)
for _ in range(100):
    a = b
    b += Vec2d(64, random.uniform(-8, 8))
    space.static_body.create_segment(a, b)
space.static_body.shapes.apply(color=pyxel.COLOR_GREEN)

class ClCdResult(NamedTuple):
    Cl: float
    Cd: float

class ClCd:
    args = property(lambda self: {"Cl": self.Cl, "Cd": self.Cd})
    
    def __init__(self, Cl_0=0.0, stall_angle=20, LD_max=10.0, Cl_max=1.0, ):
        ...

    def __call__(self, alpha):
        return ClCdResult(self.Cl(alpha), self.Cd(alpha))
        
    def __iter__(self):
        yield self.Cl
        yield self.Cd

    def Cl(self, alpha):
        ...

    def Cd(self, alpha):
        ...

    def plot(self):
        angles = np.linspace(-45, 45)

class Wing:
    def __init__(self, body, offset=(0, 0), AoA=0.0, cruise_speed=None, Cl=None, Cd=None, x_cp=0.25):
        self.body = body
        self.offset = Vec2d(*offset)
        if Cl is None and Cd is None:
            self.Cl, self.Cd = ClCd()


def make_plane():
    plane = space.create_body(10, 500)

    corpo = plane.create_poly([(-24, 0), (3, 0), (8, -2), (8, -2), (2, -4), (-2, -4)], offset=(0, 3))
    leme = plane.create_poly([(0, 0), (0, 4), (4, 0)], offset=(-23, 3))

    asa = plane.create_segment((-4, 5), (+2, 5))
    helice = plane.create_segment((9, 3), (9, -1))
    profundor = plane.create_segment((-25, 3), (-21, 3), color=pyxel.COLOR_YELLOW)

    roda = plane.create_circle(1, offset=(2, -2))
    return plane

plane = make_plane()
plane.move(50, 30)


@space.before_step()
def update():
    v: Vec2d = plane.velocity
    s = v.length
    rho = 0.1
    Cl = 0.3
    A = 1
    Cd = Cl / 10
    power = 100

    F_empuxo = 0.5 * rho * s**2 * A * Cl
    F_arrasto = - 0.5 * rho * s**2 * A * Cd
    F_motor = Vec2d(plane.mass * power, 0).rotated(0)      
    
    pt = (helice.a + helice.b) / 2
    plane.apply_force_at_local_point(F_motor, pt) 

    plane.apply_force_at_local_point((-F_arrasto, 0)) 

    plane.apply_force_at_local_point((0, F_empuxo), (1, 5)) 

    print(F_empuxo / plane.mass / 200)



@space.after_step()
def update():
    camera.follow(plane.position, tol=(64, 32))

def draw():
    pyxel.cls(0)
    space.draw()
    pyxel.text(0, 0, f"v: {plane.velocity.length:n}", pyxel.COLOR_WHITE)

pyxel.run(lambda: space.step(1/30, 2), draw)