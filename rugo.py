from pygame.math import Vector2 as Vec
from time import perf_counter
import pygame as pg

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

    def render_animation(self, fps=60, t=30):
        self.cam_h = 20 + 2
        # tail = 0
        fps = 60
        dt = 1 / fps
        lag = 10
        surf = pg.Surface((1080, 1920))
        # surf = pg.Surface((1440, 1920))

        n_frames = t * fps
        for i in range(n_frames):
            print(f"{i / n_frames:.2%}", i)
            self.render(surf)
            pg.image.save(surf, f"insta_frames/{i:04}.png")
            lag += dt
            while lag >= self.sim.dt:
                lag -= self.sim.dt

                # tail += self.sim.dt

                self.elapsed += self.sim.dt

                # a = self.sim.bodies[0].vel.x
                self.sim.step()
                # b = self.sim.bodies[0].vel.x
                # if (a > 0) and (b <= 0):
                #     print(self.i, self.elapsed)
                #     self.i += 1

                # if tail < self.tail_t:
                #     continue

                # tail -= self.tail_t

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

            # print(self.elapsed)

            # while lag > 0.1:
            #     print("oof", lag, m)
            #     lag -= 0.1

            # update simulation
            while not self.paused and lag >= self.sim.dt:
                lag -= self.sim.dt

                tail += self.sim.dt

                self.elapsed += self.sim.dt

                self.sim.step()

                if tail < self.tail_t:
                    continue

                tail -= self.tail_t

                for body in self.sim.bodies:
                    if not body.track:
                        continue

                    if body not in self.tails:
                        self.tails[body] = []

                    self.tails[body].insert(0, Vec(body.pos))

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

            elif ev.key == pg.K_l:
                # self.sim.step()
                self.paused = False

            elif ev.key == pg.K_p:
                print(self.cam_pos)
                print(self.elapsed)

        elif ev.type == pg.KEYUP:
            if ev.key == pg.K_l:
                self.paused = True

    def render(self, surf: pg.Surface):
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

        # for spr in self.sim.springs:
        #     a = sim_to_screen(spr.body_a.pos)
        #     b = sim_to_screen(spr.body_b.pos)
        #
        #     # points = [a] + [] + [b]
        #     # n = 3
        #     # for i in range(n):
        #     #     s = (i % 2) * 2 - 1
        #
        #     # pg.draw.aaline(surf, 0x4C4F69, a, b, int(0.2 * upx))
        #     # pg.draw.aaline(surf, 0xDF8E1D, a, b, int(0.1 * upx))
        #     w = int(0.1 * upx)
        #     w = max(2, w)
        #     # pg.draw.aaline(surf, 0x5C5F77, a, b, w)
        #     pg.draw.aaline(surf, 0x9CA0A4, a, b, w)

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

