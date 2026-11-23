import argparse
import sys
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication
from pet.window import PetWindow

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--smoke-test', action='store_true', help='Launch and exit after 3 seconds')
    parser.add_argument('--chat', action='store_true', help='Open the chat window at launch')
    args = parser.parse_args()
    app = QApplication(sys.argv[:1])
    app.setApplicationName('Reze Desktop Pet')
    app.setQuitOnLastWindowClosed(False)
    app.setStyleSheet('QDialog, QTextBrowser, QLineEdit { background:#fffaff; color:#493451; } QPushButton { padding:6px 14px; }')
    pet = PetWindow()
    pet.show()
    if args.chat:
        pet.open_chat()
    app.aboutToQuit.connect(pet.close)
    if args.smoke_test:
        QTimer.singleShot(3000,app.quit)
    return app.exec()

if __name__ == '__main__':
    sys.exit(main())
