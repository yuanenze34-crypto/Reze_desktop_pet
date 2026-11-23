import json
import os
import sys
from pathlib import Path

ROOT = Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parents[1]))
DEFAULTS = dict(size=180, speed=65, animation_speed=1.0, autonomous=True, always_on_top=True)

def settings_path():
    override = os.environ.get('REZE_SETTINGS_DIR')
    return Path(override or Path(os.environ.get('LOCALAPPDATA', Path.home())) / 'RezeDesktopPet') / 'settings.json'

def sanitize(data):
    result = DEFAULTS.copy()
    if not isinstance(data, dict):
        return result
    for key, low, high in [('size', 100, 360), ('speed', 10, 180), ('animation_speed', .25, 3.0)]:
        value = data.get(key)
        if type(value) in (int, float) and low <= value <= high:
            result[key] = int(value) if key != 'animation_speed' else float(value)
    for key in ('autonomous', 'always_on_top'):
        if type(data.get(key)) is bool:
            result[key] = data[key]
    return result

def load_settings(path=None):
    try:
        return sanitize(json.loads((path or settings_path()).read_text(encoding='utf-8')))
    except (OSError, ValueError):
        return DEFAULTS.copy()

def save_settings(data, path=None):
    path = path or settings_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(sanitize(data), ensure_ascii=False, indent=2), encoding='utf-8')
    temporary.replace(path)
