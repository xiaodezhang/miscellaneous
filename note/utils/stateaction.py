from PySide6.QtGui import QAction
from PySide6.QtCore import Signal

class StateAction(QAction):
    state_changed = Signal(bool)
    def __init__(self):
        super().__init__()
        self.switch_state(True)
        self.triggered.connect(lambda: self.switch_state(not self._state))

    def switch_state(self, state: bool):
        self._state = state
        self.state_changed.emit(self._state)
