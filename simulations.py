from rugo import Body, Simulation, Spring, Vec
from math import sin, cos, pi

def simulation_1():
    a = Body(
        mass=1,
        pos=(2, 0),
        # pin=True,
        vel=Vec(0, -1),
        track=True,
    )
    b = Body(
        mass=1,
        pos=(-2, -2),
        vel=Vec(0, 1),
        track=True,
    )
    return Simulation(
        [a, b],
        [Spring(a, b, k=1e4)],
        grav=0,
    )


def simulation_2():
    c1 = Body(
        vel=Vec(0, 10),
        mass=1,
        track=True,
    )
    c2 = Body(
        pin=True,
        pos=Vec(10, 0),
    )
    springs = [Spring(c1, c2, 10, 1e0)]
    bodies = [c1, c2]
    n = 2

    for i in range(n):
        t = i / n * 2 * pi
        # v = Vec(1, 0).rotate_rad(t)
        v = Vec(cos(t), sin(t))
        body = Body(
            mass=1,
            pos=v,
            vel=v.rotate_rad(pi / 4),
            # pin=True,
            track=True,
        )
        bodies.append(body)

    springs += [Spring(c1, body, 1, 1e0) for body in bodies[2:]]

    # return bodies, springs
    return Simulation(bodies, springs, freq=4096, grav=1)


def simulation_3():
    n = 3
    bodies = []
    springs = []
    w = n - 1
    for i in range(n):
        x = i / (n - 1) * w

        # body = Body(mass=100.0 / n, pos=(1e-4 * x, x))
        body = Body(mass=1 / n, pos=(1e-2 * x, x), vel=(20 * (1 - i), 0))
        if bodies:
            prev = bodies[-1]
            springs.append(Spring(body, prev, k=1e2))

        bodies.append(body)

    # bodies[0].vel.y = 1
    # bodies[-1].vel.y = -1
    bodies[0].pin = True
    bodies[-1].track = True
    # bodies[-1].pin= True

    return Simulation(
        bodies,
        springs,
        freq=8192,
        grav=0,
    )


# 5-pointed star
def simulation_4():
    m = 8
    a = Body(m, pin=True)
    b = Body(pos=(0, 1), vel=(-m, 0), track=True)
    s = Spring(a, b, m**2)

    return Simulation([a, b], [s], grav=0, freq=1 << 5)


# tree (WIP)
# def simulation_5():
#     def tree(n, i=0):
#         for i in range(2):
#             pass
#
#         if i > 0:
#             tree(n, i - 1)
#
#     bodies, springs = tree(5)
#     return


def simulation_6():
    bodies = []
    springs = []

    def body(x, y, pin=False):
        body = Body(
            mass=0.1,
            pos=(x, y),
            pin=pin,
            # track=not pin,
        )
        bodies.append(body)
        return body

    def spring(a: Body, b: Body, k=2e4):
        if a is None or b is None:
            return

        spring = Spring(a, b, k=k)
        springs.append(spring)

    n = 16
    p1 = body(0, 0)
    p2 = body(0, 1)
    spring(p1, p2)
    for i in range(n):
        a = body(i + 1, 0)
        b = body(i + 1, 1)
        spring(p1, a)
        spring(p1, b)
        spring(p2, a)
        spring(p2, b)
        spring(a, b)
        p1 = a
        p2 = b

    bodies[0].pin = True
    bodies[1].pin = True
    # bodies[-1].pin= True
    # bodies[-2].pin= True
    # bodies[-1].track = True
    # bodies[-2].track = True
    spring(bodies[1], Body(pos=bodies[-1].pos))

    # left, right = bodies[1], bodies[-1]
    # c = body(n / 2, 0, True)
    # # c = Body(pos=((n - 1) / 2, 2))
    # spring(c, left)
    # spring(c, right)
    # # spring(left, right)
    # left.track = True
    # right.track = True

    return Simulation(bodies, springs, freq=4096)


def grid(width=4, height=4, size=1.0, k=1.0, pos=(0, 0)):
    bodies = [
        [
            Body(
                pos=(j + pos[0], -i + pos[1]),
                mass=1 / height / width,
            )
            for j in range(width)
        ]
        for i in range(height)
    ]
    springs = []

    def spring(x1, y1, x2, y2):
        a = bodies[y1][x1]
        b = bodies[y2][x2]
        s = Spring(a, b, k=k)
        springs.append(s)

    for i in range(height):
        for j in range(width):
            if j != 0:
                # -
                spring(j, i, j - 1, i)
            if i != 0:
                # |
                spring(j, i, j, i - 1)
            if j != 0 and i != 0:
                # \
                spring(j, i, j - 1, i - 1)
            if j != width - 1 and i != 0:
                # /
                spring(j, i, j + 1, i - 1)

    return bodies, springs


def simulation_7():
    # spring(0, 0, grid_width - 1, grid_height - 1, -0.3)
    # spring(0, grid_height - 1, grid_width - 1, 0, -0.3)
    # spring(0, 0, grid_width - 1, grid_height - 1)

    # body(grid_width - 1, grid_height - 1).pin = True
    # body(0, grid_height - 1).pin = True

    # body(0, 0).pin = True
    # body(grid_width - 1, 0).pin = True

    bodies, springs = grid(8, 8)

    return Simulation(
        bodies=[body for row in bodies for body in row],
        springs=springs,
        freq=4096,
        grav=3,
    )


def simulation_8():
    w = 2
    h = 8
    gap = h
    springs = []
    k = 2e3
    left, s = grid(w, h, pos=(-gap / 2 - w + 1, 0), k=k)
    springs += s
    right, s = grid(w, h, pos=(gap / 2, 0), k=k)
    springs += s

    # left[0][-1].track = True
    # right[0][0].track = True

    for s, pillar in enumerate((left, right)):
        for body in pillar[-1]:
            body.pin = True

        # for i, row in enumerate(pillar):
        #     m = s * 2 - 1
        #     f = (h - i - 1) / (h - 1)
        #     v = m * 10 * f**2
        #     for body in row:
        #         body.vel = Vec(v, 0)

    weight = Body(
        mass=1,
        pos=(0, 0),
        # vel=(4, 1),
        vel=(0, 0),
        # track=True,
        # pin=True,
    )

    springs += [
        Spring(weight, left[0][-1], k=1e5),
        Spring(weight, right[0][0], k=1e5),
        # Spring(left[0][-1], right[0][0]),
    ]

    # # pillar support
    # support_left = Body(pos=(-gap / 2 - w - h + 1, -h + 1))
    # support_right = Body(pos=(gap / 2 + w + h - 1, -h + 1))
    # springs += [
    #     Spring(left[0][0], support_left, k=1e1),
    #     Spring(right[0][-1], support_right, k=1e1),
    #     # Spring(right[0][0], support_left, k=1e2),
    #     # Spring(left[0][-1], support_right, k=1e2),
    #     # Spring(support_left, support_right),
    # ]

    def flatten(grid: list[list[Body]]):
        return [body for row in grid for body in row]

    return Simulation(
        bodies=[
            *flatten(left),
            *flatten(right),
            weight,
        ],
        springs=springs,
        # grav=0,
        freq=1 << 10,
    )


def nice():
    a = Body(pin=True)
    b = Body(
        pos=(0, 1),
        vel=(1, 0),
        track=True,
    )
    s = Spring(a, b, 1, 0.994)
    return Simulation(
        bodies=[a, b],
        springs=[s],
        freq=4,
        grav=0,
    )
