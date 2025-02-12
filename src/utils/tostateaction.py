from PySide6.QtGui import QAction
from PySide6.QtCore import Signal

class ToStateAction(QAction):
    state_to_change = Signal(bool)
    def __init__(self):
        super().__init__()
        self.switch_state(True)
        self.triggered.connect(lambda: self.state_to_change.emit(self._state))

    def switch_state(self, state: bool):
        self._state = state
