from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QLabel
from pet.physics import clamp

class SpeechBubble(QLabel):
    def __init__(self):
        super().__init__(None, Qt.WindowType.ToolTip | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setTextFormat(Qt.TextFormat.PlainText)
        self.setWordWrap(True)
        self.setFixedWidth(235)
        self.setStyleSheet('QLabel { background:#fff8ff; color:#503b5d; border:1px solid #b393c8; border-radius:14px; padding:12px; font-size:14px; }')
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.hide)

    def follow(self, pet):
        bounds = pet.available()
        x = clamp(pet.x() + (pet.width()-self.width())/2, bounds.left(), bounds.right()-self.width()+1)
        y = pet.y()-self.height()-8
        if y < bounds.top():
            y = pet.y()+pet.height()+8
        y = clamp(y, bounds.top(), bounds.bottom()-self.height()+1)
        self.move(round(x),round(y))

    def say(self, text, pet):
        self.setText(text)
        self.adjustSize()
        self.follow(pet)
        self.show()
        self.timer.start(4500)
