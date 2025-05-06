from PySide6.QtCore import Slot
from PySide6.QtWidgets import QHBoxLayout, QSplitter, QWidget
from loguru import logger

from book import Book, Note
from browser import Browser
from notelistview import NoteListView
from nvim import Nvim
from resourcelistview import ResourceListView

class NoteView(QWidget):
    def __init__(self, book: Book, nvim: Nvim):
        super().__init__()

        self._nvim = nvim
        self._book = book

        self._browser = Browser(self, book)
        self._note_list_view = NoteListView(book)
        self._resource_list_view = ResourceListView()

        self._spliter = QSplitter(self)
        layout = QHBoxLayout(self)

        layout.addWidget(self._spliter)

        self._spliter.addWidget(self._note_list_view)
        self._spliter.addWidget(self._browser)
        self._spliter.addWidget(self._resource_list_view)

        self._note_list_view.side_bar_triggered.connect(
            lambda: self._browser.show_side_note_action())

        self._resource_list_view.side_bar_triggered.connect(
            lambda: self._browser.show_side_resource_action())

        self._browser.side_note_triggered.connect(
            lambda: self._note_list_view.show()
        )
        self._browser.side_resource_triggered.connect(
            lambda: self._resource_list_view.show())

        if book.current_note:
            self.switch_note(book.current_note)

        book.current_note_modified.connect(self._on_current_note_modify)
        book.current_note_changed.connect(lambda note: self.switch_note(note))
        book.new_note.connect(lambda note: self.switch_note(note))

        self._spliter.setSizes([330, 1200, 300])

    def switch_note(self, note: Note):
        self._browser.setUrl(note.url)
        self._resource_list_view.path = note.note_folder
        self._nvim.switch(note.path)

    def reload(self):
        self._browser.reload()

    @Slot() #type: ignore
    def _on_current_note_modify(self, url: str):
        self._browser.setUrl(url)
