from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextBrowser, QLineEdit, QLabel

class ChatWindow(QWidget):
    said = Signal(str)

    def __init__(self, provider):
        super().__init__()
        self.provider = provider
        self.setWindowTitle('和蕾塞聊聊 · 离线对话')
        self.resize(390, 420)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel('蕾塞  /  REZE\n简单的离线陪伴，无需联网'))
        self.history = QTextBrowser()
        layout.addWidget(self.history)
        self.entry = QLineEdit()
        self.entry.setMaxLength(2000)
        self.entry.setPlaceholderText('说点什么，按 Enter 发送…')
        layout.addWidget(self.entry)
        self.entry.returnPressed.connect(self.send)

    def send(self):
        message = self.entry.text().strip()
        if not message:
            return
        self.entry.clear()
        # insertPlainText prevents messages from becoming HTML or remote resources.
        self.history.append('你：')
        self.history.insertPlainText(message)
        answer = self.provider.reply(message)
        self.history.append('蕾塞：')
        self.history.insertPlainText(answer)
        self.said.emit(answer)
