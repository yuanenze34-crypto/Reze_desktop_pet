from pathlib import Path
from PIL import Image

COUNTS = dict(idle=6, walk_right=6, walk_left=6, sleep=4, happy=4, shy=4, angry=4, drag=2, fall_land=6)

def validate(root):
    errors = []
    for state, count in COUNTS.items():
        files = sorted((root / state).glob('*.png'))
        if len(files) != count:
            errors.append(f'{state}: expected {count}, got {len(files)}')
        for i in range(count):
            path = root / state / f'{i:03}.png'
            try:
                with Image.open(path) as im:
                    assert im.mode == 'RGBA' and im.size == (256,256)
                    assert im.getchannel('A').getextrema() == (0,255)
                    box = im.getbbox()
                    assert box and box[0] > 0 and box[1] > 0 and box[2] < 256 and box[3] < 256
            except (OSError, AssertionError) as exc:
                errors.append(f'{path}: invalid/missing frame {exc}')
    return errors

if __name__ == '__main__':
    errors = validate(Path(__file__).resolve().parents[1] / 'assets/reze')
    print('\n'.join(errors) if errors else 'PASS: 42 frames, 256x256 RGBA, real alpha, safe margins.')
    raise SystemExit(bool(errors))
