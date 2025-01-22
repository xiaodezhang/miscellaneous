import subprocess
import signal
import os
from PySide6.QtGui import QAction, QContextMenuEvent, QCursor, QIcon, QPixmap
from PySide6.QtCore import Signal, Slot
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

class NoteListView(QWidget):
    def __init__(self, book: Book):
        super().__init__()
        self._book = book

        self._note_list = ListView()

        self._layout = QVBoxLayout(self)

        self._init_toolbar()
        self._layout.addWidget(self._note_list)

        book.new_note.connect(self._on_new_note)
        book.current_note_changed.connect(self._on_current_note_change)

        self._note_list.item_changed.connect(self._on_item_change)

        self._load()

        append_class(self, 'bg-normal')
        self._note_list.set_table_style()
        self._note_list.setStyleSheet("""
            QToolButton {
                border: none;
            }
        """)

    @Slot()
    def _on_current_note_change(self, note: Note):
        note_item = next(x for x in self._note_list 
            if isinstance(x, NoteItem) and x.note == note)
        note_item.active = True

    @Slot()
    def _on_item_change(self, item):
        assert isinstance(item, NoteItem)

        # if self._process is None:
        #     self._process = subprocess.Popen(['nvim-qt', item.note.path])
        #
        # else:
        #     os.kill(self._process.pid, signal.SIGTERM)
        #     self._process = subprocess.Popen(['nvim-qt', item.note.path])

        self._book.current_note = item.note

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
        note_item = NoteItem(note)

        self._note_list.add_item(note_item)
        note_item.removed.connect(self._on_note_item_remove)

        self._note_list.set_active(0)

    def _load(self):
        for note in self._book:
            note_item = NoteItem(note)

            self._note_list.add_item(note_item)
            note_item.removed.connect(self._on_note_item_remove)

        if self._book:
            self._note_list.set_active(0)

    @Slot()
    def _on_note_item_remove(self, note_item):
        self._book.remove_note(note_item.note)
        self._note_list.delete_item(note_item)
        logger.debug("remove note")

    @Slot()
    def _on_create_note(self):
        self._book.create_note()

    # def release(self):
    #     if self._process is not None:
    #         os.kill(self._process.pid, signal.SIGTERM)

class NoteItem(Item):
    removed = Signal(Item)
    def __init__(self, note: Note):
        super().__init__()
        self._note = note;

        layout = QHBoxLayout(self)
        name_label = QLabel(note.name)

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

        note.name_changed.connect(lambda name: name_label.setText(name))

        self._more_button.clicked.connect(
            lambda: self._more_menu.exec(QCursor.pos()))

        self._remove_action.triggered.connect(self._on_remove_trigger)

        self.active_changed.connect(lambda x: self._more_button.setVisible(x))

        self.hovered.connect(self._on_hover)

        self._more_button.setVisible(self.active)

        # append_class(self, 'square')
        self.setMaximumHeight(40)

    @Slot()
    def _on_hover(self, flag):
        self._more_button.setVisible(flag)
        if self.active:
            self._more_button.setVisible(True)

    @Slot()
    def _on_remove_trigger(self):
        self.removed.emit(self)

    @property
    def note(self):
        return self._note

    @override
    def contextMenuEvent(self, event: QContextMenuEvent):
        self._more_menu.exec(event.globalPos())
        super().contextMenuEvent(event)
