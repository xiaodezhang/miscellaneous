from PySide6.QtGui import QFocusEvent, QMouseEvent
from PySide6.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QWidget
from PySide6.QtCore import Qt, Signal, Slot
from utils import override

# class EditableLabel(QLineEdit):
#     changed = Signal(str)
#     def __init__(self, text):
#         super().__init__()
#         self.setReadOnly(True)
#         self.setProperty('class', 'unbordered bg-dark')
#         self.setText(text)
#         self.setAlignment(Qt.AlignmentFlag.AlignCenter)
#         self.returnPressed.connect(lambda: self.clearFocus())
#
#     @override
#     def mouseDoubleClickEvent(self, arg__1: QMouseEvent) -> None:
#         self.setReadOnly(False)
#         return super().mouseDoubleClickEvent(arg__1)
#
#     @override
#     def focusOutEvent(self, arg__1: QFocusEvent):
#         super().focusOutEvent(arg__1)
#         self.setReadOnly(True)
#         self.changed.emit(self.text())
#
class DoubleClickLabel(QLabel):
    double_clicked = Signal()
    @override
    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        self.double_clicked.emit()
        return super().mouseDoubleClickEvent(event)

class EditableLabel(QWidget):
    changed = Signal(str)
    def __init__(self, text):
        super().__init__()
        layout = QHBoxLayout(self)
        self._edit = QLineEdit(text)
        self._label = DoubleClickLabel(text)

        self._edit.hide()
        layout.addWidget(self._edit)
        layout.addWidget(self._label)

        self._edit.editingFinished.connect(self._on_editing_finish)
        self._label.double_clicked.connect(self._on_label_double_click)

    @Slot()
    def _on_label_double_click(self):
        self._edit.show()
        self._label.hide()

    @Slot()
    def _on_editing_finish(self):
        self._edit.hide()
        self._label.setText(self._edit.text())
        self.changed.emit(self._edit.text())
        self._label.show()

    def set_text(self, text):
        self._edit.setText(text)
        self._label.setText(text)
