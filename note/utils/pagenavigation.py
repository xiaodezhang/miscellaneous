from PySide6.QtCore import QSize, Signal
from PySide6.QtGui import QAction, QIcon, QPixmap
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QToolBar, QToolButton, QWidget
from utils import place_holder
from utils.iconbutton import IconButton
from utils.resource import url

class PageNavigation(QWidget):
    next_page_clicked = Signal()
    previous_page_clicked = Signal()
    def __init__(self):
        super().__init__()
        self._next_page_button = QToolButton()
        self._previous_page_button = QToolButton()

        self._next_page_button.setIcon(
            QPixmap(url("skip_next_24dp_EAC452_FILL1_wght400_GRAD0_opsz24.svg")))
        self._next_page_button.setIconSize(QSize(28, 28))
        self._next_page_button.setFixedSize(QSize(32, 32))
        self._next_page_button.setToolTip("下一页")

        self._previous_page_button.setIcon(
            QPixmap(url("skip_previous_24dp_EAC452_FILL1_wght400_GRAD0_opsz24.svg")))
        self._previous_page_button.setIconSize(QSize(28, 28))
        self._previous_page_button.setFixedSize(QSize(32, 32))
        self._previous_page_button.setToolTip("上一页")

        self._layout = QHBoxLayout(self)
        self._current_index_label = QLabel("2")
        self._page_count_label = QLabel("5")

        self._layout.setContentsMargins(0, 0, 0, 0)

        self._layout.addWidget(QLabel("Page"))
        self._layout.addWidget(self._current_index_label)
        self._layout.addWidget(QLabel("of"))
        self._layout.addWidget(self._page_count_label)
        self._layout.addWidget(self._previous_page_button)
        self._layout.addWidget(self._next_page_button)

        self._next_page_button.clicked.connect(self.next_page_clicked)
        self._previous_page_button.clicked.connect(self.previous_page_clicked)

        self.set_enabled()
        self.setStyleSheet("""
            QToolButton {
              border: none;
              padding: 0 0 0 0;
            }
            QToolButton:focus{
              background-color: transparent;
            }
        """)

    def set_enabled(self, next = False, previous = False):
        self._next_page_button.setEnabled(next)
        self._previous_page_button.setEnabled(previous)

    def set_current_index(self, value: int):
        self._current_index_label.setText(str(value + 1))

    def set_page_count(self, value: int):
        self._page_count_label.setText(str(value))
