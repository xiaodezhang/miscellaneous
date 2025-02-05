from pathlib import Path
import subprocess
import signal
import os
from PySide6.QtGui import QAction, QContextMenuEvent, QCursor, QIcon, QPixmap
from PySide6.QtCore import QTimer, Signal, Slot
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel, 
    QMenu,
    QToolBar,
    QToolButton,
    QVBoxLayout,
    QWidget,
)
from loguru import logger
from book import Book, Note
from utils import append_class, override, place_holder
from utils.listview import Item, ListView
from utils.resource import url 

class ResourceListView(QWidget):
    side_bar_triggered = Signal()

    def __init__(self):
        super().__init__()

        self._path = None

        self._resource_list = ListView()

        self._layout = QVBoxLayout(self)

        self._timer = QTimer(self)

        self._init_toolbar()
        self._layout.addWidget(self._resource_list)

        self._timer.timeout.connect(self._on_check_resources)

        self._timer.start(500)

        append_class(self, 'bg-normal')
        self._resource_list.set_table_style()
        self._resource_list.setStyleSheet("""
            QToolButton {
                border: none;
            }
        """)

    @property
    def path(self):
        """The path property."""
        return self._path
    @path.setter
    def path(self, value):
        self._path = value

    def _init_toolbar(self):
        self._toolbar = QToolBar(self)

        self._side_bar_action = QAction(QIcon(url("left_panel_open.svg")), 
                                        "hide", self)

        self._folder_action = QAction(QIcon(url("folder_open.svg")),
                                      'open the folder', self)

        self._toolbar.setMovable(False)

        self._toolbar.addAction(self._folder_action)
        self._toolbar.addWidget(place_holder())
        self._toolbar.addAction(self._side_bar_action)

        self._layout.addWidget(self._toolbar)

        self._side_bar_action.triggered.connect(self._on_side_bar_trigger)

    @Slot()
    def _on_side_bar_trigger(self):
        self.hide()
        self.side_bar_triggered.emit()

    @Slot()
    def _on_check_resources(self):
        if self._path is None:
            return

        resources = [x for x in self._path.iterdir() 
            if not x.name.endswith('.md')]
        
        exists = [x.path for x in self._resource_list 
            if isinstance(x, ResourceItem)]

        new_resources = [x for x in resources if x not in exists]

        removed_resource_items = [x for x in self._resource_list 
            if isinstance(x, ResourceItem) and x.path not in resources]

        for item in removed_resource_items:
            self._resource_list.delete_item(item)

        for path in new_resources:
            self._resource_list.add_item(ResourceItem(path))
        
class ResourceItem(Item):
    removed = Signal(Item)
    def __init__(self, path: Path):
        super().__init__()
        self._path = path

        layout = QHBoxLayout(self)
        name_label = QLabel(path.name)

        self._more_menu = QMenu(self)
        self._remove_action = QAction(QIcon(url('do_not_disturb_on.svg')), 
                                      'delete the note', self)

        self._more_button = QToolButton()
        self._more_action = QAction(QIcon(url('more_horiz.svg')), '', self)
        icon_label = QLabel()

        self._more_menu.addAction(self._remove_action)

        icon_label.setPixmap(QPixmap(url('news.svg')))

        self._more_button.setDefaultAction(self._more_action)

        layout.addWidget(icon_label)
        layout.addWidget(name_label)
        layout.addStretch()
        layout.addWidget(self._more_button)

        self._more_button.clicked.connect(
            lambda: self._more_menu.exec(QCursor.pos()))

        self._remove_action.triggered.connect(self._on_remove_trigger)

        self.hovered.connect(self._on_hover)

        self._more_button.setVisible(self.active)

        self.setMaximumHeight(40)

    @property
    def path(self):
        return self._path

    @Slot()
    def _on_hover(self, flag):
        self._more_button.setVisible(flag)
        if self.active:
            self._more_button.setVisible(True)

    @Slot()
    def _on_remove_trigger(self):
        self.removed.emit(self)

    @override
    def contextMenuEvent(self, event: QContextMenuEvent):
        self._more_menu.exec(event.globalPos())
        super().contextMenuEvent(event)
