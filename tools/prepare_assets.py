"""Mechanically slice generated transparent atlas; keep source alpha intact."""
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
LAYOUT = {
    'idle': [(0, i) for i in range(6)],
    'walk_right': [(1, i) for i in range(6)],
    'sleep': [(2, i) for i in range(4)],
    'drag': [(2, 4), (2, 5)],
    'happy': [(3, i) for i in range(4)],
    'shy': [(4, i) for i in range(4)],
    'angry': [(5, i) for i in range(4)],
    'fall_land': [(r, c) for r in (3, 4, 5) for c in (4, 5)],
}

def main():
    atlas = Image.open(ROOT / 'assets/source/atlas.png').convert('RGBA')
    assert atlas.getchannel('A').getextrema()[0] == 0, 'Source must have true alpha'
    width, height = atlas.size
    frames = {}
    for name, cells in LAYOUT.items():
        frames[name] = []
        for row, col in cells:
            cell = atlas.crop((round(col*width/6), round(row*height/6), round((col+1)*width/6), round((row+1)*height/6)))
            bounds = cell.getchannel('A').point(lambda a: 255 if a > 20 else 0).getbbox()
            if not bounds:
                raise ValueError(f'Empty cell: {row}, {col}')
            # Same scale for every frame; translation only aligns the baseline.
            sprite = cell.crop(bounds)
            factor = 216 / (height / 6)
            sprite = sprite.resize((round(sprite.width*factor), round(sprite.height*factor)), Image.Resampling.LANCZOS)
            frame = Image.new('RGBA', (256, 256))
            frame.alpha_composite(sprite, ((256-sprite.width)//2, 240-sprite.height))
            frames[name].append(frame)
    frames['walk_left'] = [ImageOps.mirror(f) for f in frames['walk_right']]
    preview = Image.new('RGB', (6*160, 9*180), '#eee6f3')
    draw = ImageDraw.Draw(preview)
    for row, (name, sequence) in enumerate(frames.items()):
        folder = ROOT / 'assets/reze' / name
        folder.mkdir(parents=True, exist_ok=True)
        draw.text((4, row*180+2), name, fill='#4f335d')
        for index, frame in enumerate(sequence):
            frame.save(folder / f'{index:03}.png')
            small = frame.resize((150,150))
            preview.paste(small, (index*160, row*180+23), small)
        sequence[0].save(ROOT / 'assets/source' / f'{name}.gif', save_all=True,
                         append_images=sequence[1:], duration=150, loop=0, disposal=2)
    preview.save(ROOT / 'assets/source/contact-sheet.png')
    print('Exported 42 RGBA frames, contact sheet and 9 GIF previews.')

if __name__ == '__main__':
    main()
