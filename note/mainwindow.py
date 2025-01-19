from PySide6.QtCore import QSettings, Slot
from PySide6.QtGui import QCloseEvent, QIcon
from PySide6.QtWebEngineCore import QWebEngineSettings
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QHBoxLayout, QMainWindow, QSplitter, QWidget

from book import Book
from browser import Browser
from notelistview import NoteListView
from utils.resource import url

class MainWindow(QMainWindow):
    def __init__(self, book: Book):
        super().__init__()

        self._browser = Browser(self, book)
        self._note_list_view = NoteListView(book)

        container = QWidget()
        self._spliter = QSplitter(self)
        layout = QHBoxLayout(container)

        layout.addWidget(self._spliter)

        self._spliter.addWidget(self._note_list_view)
        self._spliter.addWidget(self._browser)

        self.setCentralWidget(container)

        book.current_note_modified.connect(self._on_current_note_modify)
        book.current_note_changed.connect(
            lambda note: self._browser.setUrl(note.output.as_uri()))
        book.new_note.connect(
            lambda note: self._browser.setUrl(note.output.as_uri()))

        if book.current_note:
            self._browser.setUrl(book.current_note.output.as_uri())


        self._spliter.setSizes([300, 1200])
        self.resize(1200, 800)

        self._read_settings()

        self.setWindowTitle("Note")
        self.setWindowIcon(QIcon(url('note_stack.svg')))

    @Slot()
    def _on_current_note_modify(self, url: str):
        self._browser.setUrl(url)

    def closeEvent(self, event: QCloseEvent) -> None:
        settings = QSettings("duduhome", 'note')
        settings.setValue("geometry", self.saveGeometry())
        settings.setValue("windowState", self.saveState())

        self._note_list_view.release()

        return super().closeEvent(event)

    def _read_settings(self):
        settings = QSettings("duduhome", 'note')
        self.restoreGeometry(settings.value("geometry")) #type: ignore
        self.restoreState(settings.value("windowState")) #type: ignore

