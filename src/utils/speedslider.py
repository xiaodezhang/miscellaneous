from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout
from PySide6.QtCore import Qt, Signal

from utils.resource import url
from utils.slider import Slider

class SpeedSlider(QFrame):
    changed = Signal(int)
    def __init__(
            self
            , orientation: Qt.Orientation=Qt.Orientation.Horizontal
            , delay: bool=True
            , unit='HZ'
            , max=100
        ):
        super().__init__()
        self.setStyleSheet('''
            SpeedSlider {
                border: none;
                border-radius: 0;
            }
        ''')

        icon = QLabel()
        icon.setPixmap(QPixmap(url('speed_24dp_EFEFEF_FILL1_wght400_GRAD0_opsz24.svg')))
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._slider = Slider(
            1
            , max
            , max
            , orientation
            , unit
            , delay
        )
        if orientation is Qt.Orientation.Horizontal:
            layout = QHBoxLayout(self)
            layout.addWidget(icon)
            layout.addWidget(self._slider)
            icon.setStyleSheet('''
                QLabel {
                    border-right: 1px solid #dee2e6;
                    border-radius: 0;
                    padding-right: 10px;
                }
            ''')
            self.setMinimumWidth(280)
        else:
            layout = QVBoxLayout(self)
            layout.addWidget(self._slider)
            layout.addWidget(icon)
            icon.setStyleSheet('''
                QLabel {
                    border-top: 1px solid #dee2e6;
                    border-radius: 0;
                    padding: 0;
                    padding-top: 10px;
                }
            ''')
            self.setMinimumHeight(280)
            self.setMinimumWidth(55)
        layout.setSpacing(10)
        self._slider.changed.connect(self.changed)

    def set_value(self, value: int):
        self._slider.value = value
