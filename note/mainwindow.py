from PySide6.QtCore import QSettings, Slot
from PySide6.QtGui import QCloseEvent, QIcon
from PySide6.QtWidgets import QHBoxLayout, QMainWindow, QSplitter, QWidget
from loguru import logger

from book import Book, Note
from browser import Browser
from notelistview import NoteListView
from resourcelistview import ResourceListView
from utils.resource import url
from nvim import Nvim

class MainWindow(QMainWindow):
    def __init__(self, book: Book, nvim: Nvim):
        super().__init__()

        self._nvim = nvim

        self._browser = Browser(self, book)
        self._note_list_view = NoteListView(book)
        self._resource_list_view = ResourceListView()

        container = QWidget()
        self._spliter = QSplitter(self)
        layout = QHBoxLayout(container)

        layout.addWidget(self._spliter)

        self._spliter.addWidget(self._note_list_view)
        self._spliter.addWidget(self._browser)
        self._spliter.addWidget(self._resource_list_view)

        self.setCentralWidget(container)

        book.current_note_modified.connect(self._on_current_note_modify)
        book.current_note_changed.connect(lambda note: self._switch_note(note))
        book.new_note.connect(lambda note: self._switch_note(note))

        if book.current_note:
            self._switch_note(book.current_note)

        self._spliter.setSizes([330, 1200, 300])
        self.resize(1200, 800)

        self._read_settings()

        self.setWindowTitle("Note")
        self.setWindowIcon(QIcon(url('note_stack.svg')))

    @Slot()
    def _on_current_note_modify(self, url: str):
        self._browser.setUrl(url)

    def _switch_note(self, note: Note):
        self._browser.setUrl(note.output.as_uri())
        self._resource_list_view.path = note.note_folder
        self._nvim.switch(note.path)

    def closeEvent(self, event: QCloseEvent) -> None:
        settings = QSettings("duduhome", 'note')
        settings.setValue("geometry", self.saveGeometry())
        settings.setValue("windowState", self.saveState())

        return super().closeEvent(event)

    def _read_settings(self):
        settings = QSettings("duduhome", 'note')
        self.restoreGeometry(settings.value("geometry")) #type: ignore
        self.restoreState(settings.value("windowState")) #type: ignore

