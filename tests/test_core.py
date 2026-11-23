import json
from pathlib import Path
from pet.settings import load_settings, save_settings, DEFAULTS
from pet.physics import fall_step
from pet.state_machine import StateMachine
from pet.animation import Animation
from tools.validate_assets import validate

def test_settings_invalid_and_roundtrip(tmp_path):
    path = tmp_path / 'settings.json'
    path.write_text('{bad',encoding='utf-8')
    assert load_settings(path) == DEFAULTS
    path.write_text(json.dumps({'size':-1,'autonomous':'false','speed':float('nan')}))
    assert load_settings(path) == DEFAULTS
    values = dict(DEFAULTS,size=240,autonomous=False)
    save_settings(values,path)
    assert load_settings(path) == values

def test_fall_lands_without_overshoot():
    y,v = 0,0
    for _ in range(300):
        y,v,landed = fall_step(y,v,1/60,900)
        assert y <= 900
        if landed:
            break
    assert landed and y == 900 and v == 0

def test_drag_and_reactions_not_interrupted_by_autonomy():
    fsm = StateMachine()
    for state in ('drag','fall','land','happy'):
        fsm.enter(state)
        fsm.tick(100)
        assert fsm.state == state
    fsm.animation_done()
    assert fsm.state == 'idle'

def test_animation_finishes_and_resets():
    animation = Animation()
    assert animation.step('happy',4,1)[1]
    assert animation.step('idle',6,0) == (0,False)
    index, done = animation.step('walk_right',6,1)
    assert index == 4 and not done

def test_assets_contract():
    assert validate(Path(__file__).resolve().parents[1]/'assets/reze') == []
