FPS = dict(idle=5, walk_left=10, walk_right=10, sleep=3, happy=7, shy=6, angry=7, drag=4, fall=9, land=8)

class Animation:
    def __init__(self):
        self.state, self.index, self.elapsed, self.done = '', 0, 0.0, False

    def step(self, state, count, dt, speed=1.0):
        if state != self.state:
            self.state, self.index, self.elapsed, self.done = state, 0, 0.0, False
        self.elapsed += dt * FPS.get(state, 5) * speed
        while self.elapsed >= 1 and not self.done:
            self.elapsed -= 1
            if self.index + 1 < count:
                self.index += 1
            elif state in ('happy', 'shy', 'angry', 'land'):
                self.done = True
            elif state == 'sleep':
                self.index = max(0, count - 2)
            else:
                self.index = 0
        return self.index, self.done
