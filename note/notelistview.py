import subprocess
import signal
import os
from typing import Literal
from PySide6.QtGui import QAction, QActionGroup, QContextMenuEvent, QCursor, QIcon, QMouseEvent, QPixmap
from PySide6.QtCore import QSize, QTimer, Qt, Signal, Slot
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLCDNumber,
    QLabel, 
    QLineEdit,
    QMainWindow,
    QMenu,
    QProgressBar,
    QPushButton,
    QToolBar,
    QToolButton,
    QVBoxLayout,
    QWidget,
)
from book import Book, Note
from utils import append_class, override, place_holder
from utils.listview import Item, ListView
from utils.resource import url 

class NoteListView(QWidget):
    def __init__(self, book: Book):
        super().__init__()
        self._book = book

        self._process = None

        self._note_list = ListView()

        self._layout = QVBoxLayout(self)

        self._init_toolbar()
        self._layout.addWidget(self._note_list)

        book.new_note.connect(self._on_new_note)

        for note in book:
            self._note_list.add_item(NoteItem(note))

        self._note_list.item_changed.connect(self._on_item_change)

        if book:
            self._note_list.set_active(0)

        append_class(self, 'bg-normal')
        self._note_list.setStyleSheet("""
            QToolButton {
                border: none;
            }
        """)

    @Slot()
    def _on_item_change(self, item):
        assert isinstance(item, NoteItem)
        if self._process is None:
            self._process = subprocess.Popen(['nvim-qt', item.note.path])
        else:
            os.kill(self._process.pid, signal.SIGTERM)
            self._process = subprocess.Popen(['nvim-qt', item.note.path])

    def _init_toolbar(self):
        self._toolbar = QToolBar(self)

        self._search_action = QAction(QIcon(url("search.svg")), "search", self)

        self._side_bar_action = QAction(QIcon(url("view_sidebar.svg")),
                                        "view side bar", self)

        self._new_note_action = QAction(QIcon(url('edit_square.svg')),
                                        'add new note', self)

        self._toolbar.setMovable(False)

        self._toolbar.addAction(self._side_bar_action)
        self._toolbar.addWidget(place_holder())
        self._toolbar.addAction(self._search_action)
        self._toolbar.addAction(self._new_note_action)

        self._new_note_action.triggered.connect(lambda: self._on_create_note())

        self._layout.addWidget(self._toolbar)

    @Slot()
    def _on_new_note(self, note: Note):
        self._note_list.add_item(NoteItem(note))
        self._note_list.set_active(0)

    @Slot()
    def _on_create_note(self):
        note = self._book.create_note()

    def release(self):
        if self._process is not None:
            os.kill(self._process.pid, signal.SIGTERM)

class NoteItem(Item):
    def __init__(self, note: Note):
        super().__init__()
        self._note = note;

        layout = QHBoxLayout(self)
        name_label = QLabel(note.name)

        self._more_menu = MoreMenu(self)
        self._more_button = QToolButton()
        self._more_action = QAction(QIcon(url('more_horiz.svg')), '', self)
        icon_label = QLabel()
        icon_label.setPixmap(QPixmap(url('news.svg')))

        self._more_button.setDefaultAction(self._more_action)

        layout.addWidget(icon_label)
        layout.addWidget(name_label)
        layout.addStretch()
        layout.addWidget(self._more_button)

        note.name_changed.connect(lambda name: name_label.setText(name))

        self._more_button.clicked.connect(
            lambda: self._more_menu.exec(QCursor.pos()))

        append_class(self, 'square')
        self.setMaximumHeight(40)

    @property
    def note(self):
        return self._note

    @override
    def contextMenuEvent(self, event: QContextMenuEvent):
        self._more_menu.exec(event.globalPos())
        super().contextMenuEvent(event)

class MoreMenu(QMenu):
    delete_clicked = Signal()
    b3_clicked = Signal()
    b3t_clicked = Signal()
    preview_clicked = Signal()
    excel_export_clicked = Signal()
    def __init__(self, parent):
        super().__init__(parent)
        delete_action = QAction(
            QPixmap(url('do_not_disturb_on.svg'))
            , '删除当前视频'
            , self
        )

        self.addAction(delete_action)

        delete_action.triggered.connect(self.delete_clicked)

