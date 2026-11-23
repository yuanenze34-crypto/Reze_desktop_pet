"""Render the actual Qt widget to PNG without claiming desktop screenshot QA."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from PySide6.QtWidgets import QApplication
from pet.window import PetWindow

app = QApplication([])
pet = PetWindow()
pet.timer.stop()
pet.grab().save(str(Path(__file__).resolve().parents[1]/'assets/source/widget-preview.png'))
pet.close()
