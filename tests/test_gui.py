import pytest
from PySide6.QtCore import Qt, QPoint
from PySide6.QtWidgets import QApplication
from PySide6.QtTest import QTest
from pet.window import PetWindow
from pet.asset_manager import Assets

@pytest.fixture(scope='session')
def app():
    app = QApplication.instance() or QApplication([])
    yield app

@pytest.fixture
def pet(app, tmp_path, monkeypatch):
    monkeypatch.setenv('REZE_SETTINGS_DIR',str(tmp_path))
    window = PetWindow()
    window.settings['autonomous'] = False
    window.show()
    yield window
    window.timer.stop()
    window.click_timer.stop()
    window.close()

def test_missing_and_corrupt_assets(app,tmp_path):
    (tmp_path/'idle').mkdir()
    (tmp_path/'idle/000.png').write_bytes(b'bad png')
    assets = Assets(tmp_path)
    for state in ('idle','walk_left','sleep','fall','land'):
        assert assets.get(state) and not assets.get(state)[0].isNull()

def test_click_double_click_and_chat(pet):
    QTest.mouseClick(pet,Qt.MouseButton.LeftButton,pos=QPoint(90,90))
    QTest.qWait(QApplication.doubleClickInterval()+70)
    assert pet.machine.state in ('happy','shy','angry')
    pet.machine.enter('idle')
    QTest.mouseDClick(pet,Qt.MouseButton.LeftButton,pos=QPoint(90,90))
    QTest.mouseRelease(pet,Qt.MouseButton.LeftButton,pos=QPoint(90,90))
    QTest.qWait(QApplication.doubleClickInterval()+50)
    assert pet.chat.isVisible() and pet.machine.state == 'idle'
    pet.chat.entry.setText('你好 <b>test</b>')
    pet.chat.send()
    assert '<b>test</b>' in pet.chat.history.toPlainText()

def test_drag_fall_land_and_settings(pet):
    QTest.mousePress(pet,Qt.MouseButton.LeftButton,pos=QPoint(90,90))
    QTest.mouseMove(pet,QPoint(90,-150),delay=20)
    assert pet.machine.state == 'drag'
    QTest.mouseRelease(pet,Qt.MouseButton.LeftButton,pos=QPoint(90,90))
    assert pet.machine.state == 'fall'
    QTest.qWait(1800)
    assert pet.machine.state == 'idle'
    assert abs(pet.y()-pet.floor(pet.available())) <= 1
    pet.change('size',240)
    from pet.settings import load_settings
    assert load_settings()['size'] == 240
    assert not pet.mask().contains(QPoint(0,0))
