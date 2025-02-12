from PySide6.QtCore import QSize
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QToolButton

class IconButton(QToolButton):
    def __init__(self, path: str='', size: int=24, tips=""):
        super().__init__()
        if path:
            self.setIcon(QPixmap(path))
        self.setIconSize(QSize(size+10, size+10))
        self.setFixedSize(QSize(size+20, size+20))
        self.setToolTip(tips)
