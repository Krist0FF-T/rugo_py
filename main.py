import pygame as pg
from pygame.math import Vector2 as Vec
from time import perf_counter
import math

class Body:
    def __init__(
        self,
        mass=1.0,
        pos=(0, 0),
        vel=(0, 0),
        pin=False,
        track=False,
    ):
        self.pos = Vec(pos)
        self.vel = Vec(vel)
        self.acc = Vec()
        self.mass = mass
        self.pin = pin
        self.track = track

    def force(self, vec: Vec):
        self.acc += vec / self.mass


class Spring:
    def __init__(
        self,
        body_a: Body,
        body_b: Body,
        k: float = 1.0,
        rest_length: float | None = None,
    ):
        self.body_a = body_a
        self.body_b = body_b
        if rest_length is None:
            rest_length = (body_a.pos - body_b.pos).length()
        self.rest_length = rest_length
        self.k = k

    def force(self):
        diff = self.body_b.pos - self.body_a.pos
        dist = diff.length()
        # if dist < self.radius:
        #     return

        force = self.k * (dist - self.rest_length)
        direc = Vec(0, 1) if diff.length() == 0 else diff.normalize()
        self.body_a.force(direc * force)
        self.body_b.force(-direc * force)


class Simulation:
    def __init__(
        self,
        bodies: list[Body],
        springs: list[Spring],
        freq: float = 2048,
        grav: float = 9.81,
    ):
        self.bodies = bodies
        self.springs = springs
        self.grav = grav
        self.dt = 1 / freq

    def step(self):
        # for body in self.bodies:
        #     body.acc = Vec(0, -self.grav)

        for spring in self.springs:
            spring.force()

        for body in self.bodies:
            if body.pin:
                continue

            body.acc.y -= self.grav
            body.vel += self.dt * body.acc
            body.pos += self.dt * body.vel
            body.acc = Vec()


class Simulator:
    def __init__(self, sim: Simulation):
        self.screen = pg.display.set_mode(
            (1280, 720),
            pg.RESIZABLE,
            vsync=1,
        )
        # self.screen = None
        self.should_close = False
        self.sim = sim

        # self.cam_h = 30 + 8 + 3 * 2
        self.cam_h = 10
        self.cam_pos = Vec()
        # self.cam_pos = Vec(
        #     7 * 3 / 2,
        #     (-30 + 8) / 2,
        # )
        # self.cam_pos = sum(
        #     (body.pos.x for body in sim.bodies),
        #     Vec(0, 0),
        # ) / len(sim.bodies)

        self.tails = dict()
        self.paused = True
        self.frame_count = 0
        self.tail_t = 0.05
        self.elapsed = 0
        self.i = 0

    def render_animation(self):
        self.cam_h = 20 + 2
        tail = 0
        fps = 60
        dt = 1 / fps
        lag = 10
        surf = pg.Surface((1080, 1920))
        # surf = pg.Surface((1440, 1920))

        # n_frames = 30 * fps
        n_frames = 2
        for i in range(n_frames):
            print(f"{i / n_frames:.2%}", i)
            self.render(surf)
            pg.image.save(surf, f"insta_frames/{i:04}.png")
            lag += dt
            while lag >= self.sim.dt:
                lag -= self.sim.dt

                tail += self.sim.dt

                self.elapsed += self.sim.dt

                # a = self.sim.bodies[0].vel.x
                self.sim.step()
                # b = self.sim.bodies[0].vel.x
                # if (a > 0) and (b <= 0):
                #     print(self.i, self.elapsed)
                #     self.i += 1

                if tail < self.tail_t:
                    continue

                tail -= self.tail_t

                for body in self.sim.bodies:
                    if not body.track:
                        continue

                    if body not in self.tails:
                        self.tails[body] = []

                    self.tails[body].insert(0, Vec(body.pos))
                    # if len(self.tails[body]) >= 30 / self.tail_t * 2:
                    #     self.paused = True

    def run(self):
        lag = 0
        t_prev = perf_counter()
        tail = self.tail_t
        # self.render_animation()
        # exit()

        while not self.should_close:
            self.frame_count += 1
            now = perf_counter()
            dt = now - t_prev
            t_prev = now
            if not self.paused:
                lag += dt

            for ev in pg.event.get():
                self.handle_event(ev)

            keys = pg.key.get_pressed()
            self.cam_h += dt * self.cam_h * (keys[pg.K_DOWN] - keys[pg.K_UP])
            self.cam_pos.x += dt * self.cam_h * (keys[pg.K_d] - keys[pg.K_a])
            self.cam_pos.y += dt * self.cam_h * (keys[pg.K_w] - keys[pg.K_s])

            print(self.elapsed)

            # while lag > 0.1:
            #     print("oof", lag, m)
            #     lag -= 0.1

            # update simulation
            while not self.paused and lag >= self.sim.dt:
                lag -= self.sim.dt

                tail += self.sim.dt

                self.elapsed += self.sim.dt

                # a = self.sim.bodies[0].vel.x
                self.sim.step()
                # b = self.sim.bodies[0].vel.x
                # if (a > 0) == (b < 0):
                #     print(self.i, self.elapsed)
                #     self.i += 1

                if tail < self.tail_t:
                    continue

                tail -= self.tail_t

                for body in self.sim.bodies:
                    if not body.track:
                        continue

                    if body not in self.tails:
                        self.tails[body] = []

                    self.tails[body].insert(0, Vec(body.pos))
                    # if len(self.tails[body]) >= 30 / self.tail_t * 2:
                    #     self.paused = True

            self.render(self.screen)
            pg.display.update()

    def handle_event(self, ev: pg.Event):
        if ev.type == pg.QUIT:
            self.should_close = True

        elif ev.type == pg.KEYDOWN:
            if ev.key == pg.K_ESCAPE:
                self.should_close = True

            elif ev.key == pg.K_SPACE:
                self.paused = not self.paused

            elif ev.key == pg.K_g:
                surf = pg.Surface((2356, 3840))
                self.render(surf)
                pg.image.save(surf, "screenshot.png")

            elif ev.key == pg.K_p:
                print(self.cam_pos)
                print(self.elapsed)

    def render(self, surf):
        # fade = pg.Surface(surf.size)
        # fade.fill(0x26292C)
        # fade.set_alpha(10)
        # surf.blit(fade)

        surf.fill(0x26292C)

        # surf.fill(0xEFF1F5)
        # upx = min(surf.size) / self.cam_h
        upx = surf.height / self.cam_h

        def sim_to_screen(p):
            p = Vec(p)
            return Vec(
                surf.size[0] / 2 + (p.x - self.cam_pos.x) * upx,
                surf.size[1] / 2 - (p.y - self.cam_pos.y) * upx,
            )

        # def screen_to_sim(p):
        #     p = Vec(p)
        #     return Vec(
        #         (p.x - surf.size[0] / 2) / upx + self.cam_pos.x,
        #         (p.y - surf.size[1] / 2) / upx + self.cam_pos.y,
        #     )

        # top_left = screen_to_sim(Vec(0, 0))
        # bottom_right = screen_to_sim(surf.size)
        # # print(top_left, bottom_right)
        # for i in range(int(top_left.x), int(bottom_right.x) + 1):
        #     x = sim_to_screen(Vec(i, 0)).x
        #     pg.draw.aaline(
        #         surf,
        #         # 0x4C4F69,
        #         0x26292C * 2,
        #         (x, 0),
        #         (x, surf.height),
        #     )

        # for i in range(int(top_left.y), int(bottom_right.y) + 1):
        #     y = sim_to_screen(Vec(0, i)).y
        #     pg.draw.aaline(
        #         surf,
        #         # 0x4C4F69,
        #         0x26292C * 2,
        #         (0, y),
        #         (surf.width, y),
        #     )

        for body, tail in self.tails.items():
            if len(tail) < 2:
                continue
            # tail = tail[:8]

            points = [
                sim_to_screen(p)
                # sim_to_screen(
                #     (p.x, -self.tail_t * i - self.elapsed % self.tail_t),
                # )
                for i, p in enumerate(tail)
            ]
            w = max(2, int(0.01 * upx))
            pg.draw.lines(surf, 0xF8F8F2, False, points, w)

        # for spr in self.sim.springs:
        #     a = sim_to_screen(spr.body_a.pos)
        #     b = sim_to_screen(spr.body_b.pos)
        #     # pg.draw.aaline(surf, 0x4C4F69, a, b, int(0.2 * upx))
        #     # pg.draw.aaline(surf, 0xDF8E1D, a, b, int(0.1 * upx))
        #     w = int(0.1 * upx)
        #     w = max(2, w)
        #     # pg.draw.aaline(surf, 0x5C5F77, a, b, w)
        #     pg.draw.aaline(surf, 0x9CA0A4, a, b, w)
        #
        #     # ap, bp = spr.body_a.pin, spr.body_b.pin
        #     # c = a if (ap and not bp) else b if (bp and not ap) else None
        #     # if c is not None:
        #     #     pg.draw.aacircle(surf, 0xAAAAAA, c, spr.radius * upx, 3)
        #
        #     # pg.draw.aacircle(surf, 0xAAAAAA, a, spr.radius * upx, 3)
        #     # pg.draw.aacircle(surf, 0xAAAAAA, b, spr.radius * upx, 3)

        for spr in self.sim.springs:
            a = sim_to_screen(spr.body_a.pos)
            b = sim_to_screen(spr.body_b.pos)

            # points = [a] + [] + [b]
            # n = 3
            # for i in range(n):
            #     s = (i % 2) * 2 - 1

            # pg.draw.aaline(surf, 0x4C4F69, a, b, int(0.2 * upx))
            # pg.draw.aaline(surf, 0xDF8E1D, a, b, int(0.1 * upx))
            w = int(0.1 * upx)
            w = max(2, w)
            # pg.draw.aaline(surf, 0x5C5F77, a, b, w)
            pg.draw.aaline(surf, 0x9CA0A4, a, b, w)

        for body in self.sim.bodies:
            o = sim_to_screen(body.pos)
            r = 0.1 * upx
            pg.draw.aacircle(surf, 0x66D9EF, o, r)
            # if self.frame_count % 2 == 0 and body.track and not self.paused:
            #     if body not in self.tails:
            #         self.tails[body] = []
            #     self.tails[body].insert(0, Vec(body.pos))

        if self.paused and surf == self.screen:
            pg.draw.rect(surf, "white", (30, 30, 10, 30))
            pg.draw.rect(surf, "white", (50, 30, 10, 30))


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
        t = i / n * 2 * math.pi
        # v = Vec(1, 0).rotate_rad(t)
        v = Vec(math.cos(t), math.sin(t))
        body = Body(
            mass=1,
            pos=v,
            vel=v.rotate_rad(math.pi / 4),
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


if __name__ == "__main__":
    sim = simulation_4()
    Simulator(sim).run()
