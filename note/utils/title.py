from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QHBoxLayout, QLabel, QFrame

class Title(QFrame):
    def __init__(self, name: str, path: str=""):
        super().__init__()
        self.setStyleSheet("""
            Title {
              background-color:#495057;
              border: none;
              border-radius: none;
              padding: 0px;
            }
            Title > QLabel {
              color: white;
            }
        """)
        layout = QHBoxLayout(self)
        layout.setSpacing(6)
        layout.setContentsMargins(3, 0, 3, 0)
        if path:
            icon = QLabel()
            pixmap = QPixmap(path)
            icon.setPixmap(pixmap)
            layout.addWidget(icon)
        layout.addWidget(QLabel(name))
        layout.addStretch()
