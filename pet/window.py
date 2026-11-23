import random
from PySide6.QtCore import Qt, QTimer, QElapsedTimer, QPoint
from PySide6.QtGui import QPainter, QGuiApplication, QRegion, QIcon
from PySide6.QtWidgets import QWidget, QApplication, QMenu, QSystemTrayIcon, QDialog
from pet.settings import load_settings, save_settings
from pet.asset_manager import Assets
from pet.animation import Animation
from pet.state_machine import StateMachine, REACTIONS
from pet.physics import clamp, fall_step
from ai.local_provider import LocalProvider
from ui.chat_window import ChatWindow
from ui.speech_bubble import SpeechBubble
from ui.settings_window import SettingsWindow

class PetWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.settings = load_settings()
        self.assets, self.animation, self.machine = Assets(), Animation(), StateMachine()
        self.provider = LocalProvider()
        self.bubble = SpeechBubble()
        self.chat = ChatWindow(self.provider)
        self.chat.said.connect(lambda text: self.bubble.say(text,self))
        self.paused = False
        self.menu_open = False
        self.pressed = False
        self.dragging = False
        self.suppress_release = False
        self.velocity = 0.0
        self.px, self.py = 0.0, 0.0
        self.pixmap = None
        self.render_key = None
        self.setWindowTitle('Reze Desktop Pet')
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.apply_settings(self.settings, persist=False)
        bounds = self.available()
        self.px = bounds.right()-self.width()-80
        self.py = self.floor(bounds)
        self.move(round(self.px),round(self.py))
        self.click_timer = QTimer(self)
        self.click_timer.setSingleShot(True)
        self.click_timer.timeout.connect(self.react)
        self.clock = QElapsedTimer()
        self.clock.start()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.tick)
        self.timer.start(16)
        self.tray = QSystemTrayIcon(QIcon(self.assets.get('idle')[0]),self)
        self.tray.setToolTip('蕾塞桌宠 · 双击聊天，右键菜单')
        self.tray.activated.connect(self.tray_activated)
        self.tray.setContextMenu(self.make_menu())
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.tray.show()
        QGuiApplication.instance().screenRemoved.connect(self.rescue)
        self.tick()

    def available(self):
        screen = QGuiApplication.screenAt(self.frameGeometry().center()) or QGuiApplication.primaryScreen()
        return screen.availableGeometry()

    def floor(self, bounds):
        # Exported frames share a baseline at y=240 / 256.
        return bounds.bottom()+1-round(self.height()*240/256)

    def rescue(self, *_):
        bounds = self.available()
        self.px = clamp(self.px,bounds.left(),bounds.right()-self.width()+1)
        self.py = clamp(self.py,bounds.top(),self.floor(bounds))
        self.move(round(self.px),round(self.py))

    def apply_settings(self, values, persist=True):
        self.settings = values.copy()
        flags = Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool
        if values['always_on_top']:
            flags |= Qt.WindowType.WindowStaysOnTopHint
        self.setWindowFlags(flags)
        self.setFixedSize(values['size'],values['size'])
        self.render_key = None
        if persist:
            self.rescue()
            self.show()
            try:
                save_settings(values)
            except OSError:
                self.bubble.say('设置暂时无法写入磁盘，本次仍然生效。',self)

    def tick(self):
        dt = min(self.clock.restart()/1000, .05)
        if self.menu_open:
            return
        state = self.machine.state
        bounds = self.available()
        if state == 'fall':
            self.py,self.velocity,landed = fall_step(self.py,self.velocity,dt,self.floor(bounds))
            if landed:
                self.machine.enter('land')
        elif not self.dragging and not self.pressed:
            self.py = self.floor(bounds)
            if not self.paused:
                self.machine.tick(dt,self.settings['autonomous'])
                state = self.machine.state
                if state in ('walk_left','walk_right') and self.settings['autonomous']:
                    self.px += (-1 if state == 'walk_left' else 1)*self.settings['speed']*dt
                    if self.px <= bounds.left():
                        self.px = bounds.left()
                        self.machine.enter('walk_right')
                    elif self.px >= bounds.right()-self.width()+1:
                        self.px = bounds.right()-self.width()+1
                        self.machine.enter('walk_left')
        if not self.dragging:
            self.px = clamp(self.px,bounds.left(),bounds.right()-self.width()+1)
            self.move(round(self.px),round(self.py))
        state = self.machine.state
        frames = self.assets.get(state)
        index,done = self.animation.step(state,len(frames),dt,self.settings['animation_speed'])
        key = (state,index,self.width())
        if key != self.render_key:
            self.render_key = key
            self.pixmap = frames[index].scaled(self.size(),Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation)
            # Native window region excludes transparent pixels from mouse hit testing.
            self.setMask(QRegion(self.pixmap.mask()))
            self.update()
        if done:
            self.machine.animation_done()
        if self.bubble.isVisible():
            self.bubble.follow(self)

    def paintEvent(self,event):
        if self.pixmap:
            painter = QPainter(self)
            painter.drawPixmap(0,0,self.pixmap)

    def mousePressEvent(self,event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.pressed = True
            self.press_point = event.globalPosition().toPoint()
            self.offset = self.press_point-self.pos()
            self.dragging = False

    def mouseMoveEvent(self,event):
        if not self.pressed:
            return
        current = event.globalPosition().toPoint()
        if not self.dragging and (current-self.press_point).manhattanLength() >= QApplication.startDragDistance():
            self.click_timer.stop()
            self.dragging = True
            self.machine.enter('drag')
        if self.dragging:
            pos = current-self.offset
            screen = QGuiApplication.screenAt(current) or QGuiApplication.primaryScreen()
            bounds = screen.availableGeometry()
            self.px = clamp(pos.x(),bounds.left(),bounds.right()-self.width()+1)
            self.py = clamp(pos.y(),bounds.top(),self.floor(bounds))
            self.move(round(self.px),round(self.py))

    def mouseReleaseEvent(self,event):
        if event.button() != Qt.MouseButton.LeftButton:
            return
        self.pressed = False
        if self.dragging:
            self.dragging = False
            self.velocity = 0
            self.machine.enter('fall')
        elif self.suppress_release:
            self.suppress_release = False
        else:
            self.click_timer.start(QApplication.doubleClickInterval())

    def mouseDoubleClickEvent(self,event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.click_timer.stop()
            self.suppress_release = True
            self.open_chat()

    def react(self):
        if self.machine.state in ('drag','fall','land'):
            return
        state = random.choice(REACTIONS)
        self.machine.enter(state)
        self.bubble.say(self.provider.phrase(state),self)

    def open_chat(self):
        self.chat.show()
        self.chat.raise_()
        self.chat.activateWindow()
        self.chat.entry.setFocus()

    def set_paused(self,value):
        self.paused = value
        if self.machine.state not in ('drag','fall','land'):
            self.machine.enter('idle')

    def change(self,key,value):
        values = self.settings.copy()
        values[key] = value
        self.apply_settings(values)

    def settings_dialog(self):
        dialog = SettingsWindow(self.settings,self)
        self.menu_open = True
        try:
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.apply_settings(dialog.values())
        finally:
            self.menu_open = False

    def make_menu(self):
        menu = QMenu(self)
        menu.addAction('和蕾塞聊聊',self.open_chat)
        menu.addSeparator()
        menu.addAction('暂停自主活动',lambda: self.set_paused(True))
        menu.addAction('恢复自主活动',lambda: self.set_paused(False))
        size = menu.addMenu('角色大小')
        for number in (120,180,240,300):
            size.addAction(f'{number} px',lambda n=number: self.change('size',n))
        menu.addAction('切换置顶',lambda: self.change('always_on_top',not self.settings['always_on_top']))
        menu.addAction('设置…',self.settings_dialog)
        menu.addSeparator()
        menu.addAction('退出',QApplication.instance().quit)
        return menu

    def contextMenuEvent(self,event):
        self.click_timer.stop()
        menu = self.make_menu()
        self.menu_open = True
        try:
            menu.exec(event.globalPos())
        finally:
            self.menu_open = False
            menu.deleteLater()

    def tray_activated(self,reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.open_chat()

    def closeEvent(self,event):
        self.bubble.close()
        self.chat.close()
        self.tray.hide()
        super().closeEvent(event)
