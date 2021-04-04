import pyxel
from easymunk import pyxel as phys, Vec2d, Body, Transform

svg1 = """0,0 -53.8281,34.3789 -233.3594,390.41211 -13.0625,84.15821 
18.9492,39.89453 41.9531,33.78125 58.3926,7.60156 360.1621,-80.88086 
10.4414,-29.35351 -30.9316,-38.56836 -81.6328,-11.84571 -31.8692,-15.77148 
-75.6406,-74.07617 -16.5508,-32.27735 -14.1894,-92.73632 7.2344,-37.69532 
40.5253,-68.98828 72.9473,-23.23047 53.0781,23.90039 26.7383,24.73633 
27.0625,49.43164 26.8281,4.06445 4.336,-13.25585 -30.9082,-120.7793 
-46.5352,-47.08789"""

svg2 = """-20,-90 -0.084,0.05469 -0.059,0.03711
-26.8256,17.133238 -53.6502,34.268288 -80.4765,51.400388 -82.0089,137.20093 
-164.0166,274.40256 -246.0254,411.60352 -5.8273,37.54235 -11.6546,75.0847 
-17.4825,112.62695 10.7157,22.55662 21.427,45.11529 32.1426,67.67188 
21.5702,17.37016 43.143,34.73697 64.7129,52.10742 28.1465,3.66431 
56.2929,7.32901 84.4395,10.99219 133.6336,-30.01177 267.2676,-60.02205 
400.9023,-90.0293 10.5835,-29.75342 21.1676,-59.50664 31.752,-89.25977 
-21.6888,-27.0418 -43.3775,-54.08367 -65.0645,-81.12695 -34.6604,-5.02848 
-69.3203,-10.06014 -103.9805,-15.08984 -25.2135,-24.69206 -50.427,-49.38412 
-75.6406,-74.07618 -4.7298,-30.9121 -9.4596,-61.82421 -14.1894,-92.73632 
13.5084,-22.9961 27.0169,-45.99219 40.5254,-68.98829 53.0781,23.9004 
13.5633,24.77397 27.1251,49.54883 40.6894,74.32226 34.2865,5.19505 
68.5727,10.39215 102.8594,15.58594 8.204,-25.07741 16.4051,-50.15578
24.6055,-75.23438 -12.9661,-50.65835 -25.9287,-101.31763 -38.8926,-151.97656 
-24.3791,-24.67169 -48.7627,-49.33886 -73.1406,-74.01172 -53.5573,-2.59054 
-107.1146,-5.183 -160.6719,-7.773435"""


def parse(path):
    for pt in path.split():
        x, _, y = pt.partition(",")
        yield Vec2d(float(x), float(y))


def make_paths(svg, body: Body, transform=Transform.identity(), **kwargs):
    a, *bs = map(transform, parse(svg))
    paths = []
    for b in bs:
        b += a
        paths.append(body.create_segment(a, b, **kwargs))
        a = b
    a = paths[-1].b
    b = paths[0].a
    paths.append(body.create_segment(a, b, **kwargs))
    return paths


pyxel.init(256, 196)
camera = phys.Camera(flip_y=True)
space = phys.space(camera=camera, damping=0.75, friction=1.0, elasticity=0.0, sub_steps=4)

make_paths(svg1, space.static_body, Transform.scaling(2), color=pyxel.COLOR_WHITE)
make_paths(svg2, space.static_body, Transform.scaling(1), color=pyxel.COLOR_WHITE)


def make_car(space, x, y, keys, color):
    car = phys.rect(x, y, 20, 7, mass=1, moment=10, friction=1.0, color=color)

    @space.before_step()
    def _():
        airspeed = car.velocity.dot(car.rotation_vector)
        r = 1 if airspeed == 0 else max(1 - airspeed / 300, 0)

        turn, F = phys.arrow(-250, 150 * car.mass * r, keys)
        car.apply_force_at_local_point(Vec2d(F, 0), (-15, 0))

        k = 2.0
        car.torque += k * (turn - car.angular_velocity)

        k = car.mass * 0.25
        Fy = k * car.velocity.cross(car.rotation_vector)
        Fx = -k * car.velocity.dot(car.rotation_vector)
        car.apply_force_at_local_point((Fx, Fy), (-8, 0))

    return car


car1 = make_car(space, 0, -50, "arrows", color=pyxel.COLOR_RED)
car2 = make_car(space, 0, -75, "adws", color=pyxel.COLOR_YELLOW)
car3 = make_car(space, 0, -25, "jlik", color=pyxel.COLOR_CYAN)
camera.follow((car1.position + car2.position) / 2)


@space.after_step()
def _():
    camera.offset += (car1.velocity + car2.velocity) / 60 / 4
    camera.follow((car1.position + car2.position) / 2, (120, 90))


space.run()
