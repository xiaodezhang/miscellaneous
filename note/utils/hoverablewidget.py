from PySide6.QtCore import QEvent, Signal
from PySide6.QtGui import QEnterEvent
from PySide6.QtWidgets import QFrame, QWidget

from utils import append_class, remove_class

class HoverableWidget(QFrame):
    hovered = Signal(bool)
    def __init__(self):
        super().__init__()
        self.setProperty('class', 'hoverable unbordered')

    def set_hovered(self, flag=True):
        if flag:
            append_class(self, 'hovered')
        else:
            remove_class(self, 'hovered')

    def enterEvent(self, event: QEnterEvent) -> None:
        self._hovered = True
        self.hovered.emit(True)
        return super().enterEvent(event)

    def leaveEvent(self, event: QEvent) -> None:
        self._hovered = False
        self.hovered.emit(False)
        return super().leaveEvent(event)
