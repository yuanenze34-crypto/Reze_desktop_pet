from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPixmap, QPainter, QColor
from pet.settings import ROOT

class Assets:
    def __init__(self, root=None):
        self.root = root or ROOT / 'assets/reze'
        self.cache = {}
        self.fallback = QPixmap(256,256)
        self.fallback.fill(Qt.GlobalColor.transparent)
        painter = QPainter(self.fallback)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QColor('#715185'))
        painter.drawEllipse(QRectF(48, 40, 160, 185))
        painter.setPen(Qt.GlobalColor.white)
        painter.drawText(self.fallback.rect(), Qt.AlignmentFlag.AlignCenter, 'Reze\n素材缺失')
        painter.end()

    def get(self, state):
        if state in self.cache:
            return self.cache[state]
        folder = 'fall_land' if state in ('fall', 'land') else state
        frames = []
        for path in sorted((self.root / folder).glob('*.png')):
            pix = QPixmap(str(path))
            if not pix.isNull():
                frames.append(pix.scaled(256,256,Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation))
        if state == 'fall':
            frames = frames[:3]
        elif state == 'land':
            frames = frames[3:] or frames[-1:]
        if not frames and state == 'walk_left':
            from PySide6.QtGui import QTransform
            frames = [p.transformed(QTransform().scale(-1,1)) for p in self.get('walk_right')]
        if not frames:
            frames = self.get('idle') if state != 'idle' else [self.fallback]
        self.cache[state] = frames
        return frames
