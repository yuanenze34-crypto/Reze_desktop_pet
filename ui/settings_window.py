from PySide6.QtWidgets import QDialog, QFormLayout, QSpinBox, QDoubleSpinBox, QCheckBox, QDialogButtonBox

class SettingsWindow(QDialog):
    def __init__(self, settings, parent):
        super().__init__(parent)
        self.setWindowTitle('蕾塞 · 设置')
        form = QFormLayout(self)
        self.controls = {}
        for key, label, low, high in [('size','角色大小',100,360),('speed','行走速度',10,180),('animation_speed','动画速度',.25,3.0)]:
            control = QDoubleSpinBox() if key == 'animation_speed' else QSpinBox()
            control.setRange(low, high)
            control.setValue(settings[key])
            form.addRow(label,control)
            self.controls[key] = control
        for key, label in [('autonomous','自主活动'),('always_on_top','始终置顶')]:
            control = QCheckBox()
            control.setChecked(settings[key])
            form.addRow(label,control)
            self.controls[key] = control
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        form.addRow(buttons)

    def values(self):
        return {k: (v.isChecked() if isinstance(v,QCheckBox) else v.value()) for k,v in self.controls.items()}
