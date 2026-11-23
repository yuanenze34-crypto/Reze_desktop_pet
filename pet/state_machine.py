import random

REACTIONS = ('happy', 'shy', 'angry')
STATES = ('idle', 'walk_left', 'walk_right', 'sleep', *REACTIONS, 'drag', 'fall', 'land')

class StateMachine:
    def __init__(self):
        self.state = 'idle'
        self.elapsed = 0.0
        self.duration = 4.0

    def enter(self, state):
        if state not in STATES:
            raise ValueError(state)
        self.state, self.elapsed = state, 0.0
        self.duration = random.uniform(3, 7) if state != 'sleep' else random.uniform(12, 22)

    def tick(self, dt, autonomous=True):
        self.elapsed += dt
        if autonomous and self.state in ('idle', 'walk_left', 'walk_right', 'sleep') and self.elapsed >= self.duration:
            self.enter(random.choice(('idle', 'walk_left', 'walk_right', 'sleep')) if self.state == 'idle' else 'idle')

    def animation_done(self):
        if self.state in (*REACTIONS, 'land'):
            self.enter('idle')
