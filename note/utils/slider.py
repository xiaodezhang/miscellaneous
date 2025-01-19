from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QSlider, QVBoxLayout
from PySide6.QtCore import QTime, QTimer, Qt, Signal
from loguru import logger

# 该控件可用于和设备交互，我们降低它的设置频率
class Slider(QFrame):
    changed = Signal(int)
    def __init__(
            self
            , min: int
            , max: int
            , default: int=0
            , orientation: Qt.Orientation=Qt.Orientation.Horizontal
            , unit: str=''
            , delay: bool=True
        ):
        super().__init__()
        self.setStyleSheet("border:none; margin: 0; padding: 0;")
        self._unit = unit

        self._label = QLabel(f'{default}{unit}')
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._slider = QSlider(orientation)
        self._slider.setMaximum(max)
        self._slider.setMinimum(min)
        self._slider.setValue(default)

        self._value = default 
        if orientation is Qt.Orientation.Horizontal:
            layout = QHBoxLayout(self)
            layout.addWidget(self._label)
            layout.addWidget(self._slider)
            self._label.setMinimumWidth(40)
        else:
            layout = QVBoxLayout(self)
            slider_layout = QHBoxLayout()
            slider_layout.addStretch()
            slider_layout.addWidget(self._slider)
            slider_layout.addStretch()
            layout.addLayout(slider_layout)
            layout.addWidget(self._label)
            # self._label.setMinimumWidth(20)

        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(10)
        layout.setContentsMargins(0, 0, 0, 0)

        if delay:
            self._timer = QTimer(self)
            def on_timeout():
                value = self._slider.value()
                self._label.setText(f'{value}{unit}')
                if value != self._value:
                    self.changed.emit(value)
                    self._value = value
            self._timer.timeout.connect(on_timeout)
            self._timer.start(1000)
            self._slider.valueChanged.connect(lambda x: self._label.setText(f'{x}{self._unit}'))
        else:
            def on_slider_value_change(value: int):
                self._value = value
                self._label.setText(f'{value}{unit}')
                self.changed.emit(value)
            self._slider.valueChanged.connect(on_slider_value_change)

    @property
    def value(self):
        return self._value
    @value.setter
    def value(self, v):
        if self._value == v:
            return
        self._slider.setValue(v)
