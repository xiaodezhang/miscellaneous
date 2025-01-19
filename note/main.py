import re
import subprocess
import hashlib
import os
from pathlib import Path
import sys
from PySide6.QtCore import QSettings, QTimer, Slot
from PySide6.QtGui import QAction, QCloseEvent, QIcon
from PySide6.QtWebEngineCore import QWebEngineSettings
from PySide6.QtWidgets import QApplication, QHBoxLayout, QMainWindow, QSplitter, QToolBar, QVBoxLayout, QWidget
from PySide6.QtWebEngineWidgets import QWebEngineView
from loguru import logger
from qt_material import apply_stylesheet
from uuid import uuid4

from book import Book
from notelistview import NoteListView
from utils.resource import url
from utils import append_class, place_holder

def get_file_hash(file_path):
    hash_sha256 = hashlib.sha256()

    with open(file_path, 'rb') as f:
        while chunk := f.read(4096):
            hash_sha256.update(chunk)

    return hash_sha256.hexdigest()

def get_file_title(file_path):
    title = ''

    with open(file_path) as f:
        line = f.readline()
        mathches = re.findall(r"^#\s*(.+)", line)
        if mathches:
            title = mathches[0]

    return title

class MainWidget(QMainWindow):
    def __init__(self, book: Book):
        super().__init__()

        self._note_list_view = NoteListView(book)

        container = QWidget()
        self._spliter = QSplitter(self)
        layout = QHBoxLayout(container)

        layout.addWidget(self._spliter)
        self._spliter.addWidget(self._note_list_view)

        self._build_browser()

        self.setCentralWidget(container)

        book.current_note_modified.connect(self._on_current_note_modify)
        book.current_note_changed.connect(
            lambda note: self._browser.setUrl(note.output.as_uri()))

        if book.current_note:
            self._browser.setUrl(book.current_note.output.as_uri())

        self._read_settings()

        self._spliter.setSizes([300, 1100])
        self.resize(1200, 800)

        self.setWindowTitle("Note")
        self.setWindowIcon(QIcon(url('note_stack.svg')))

    @Slot()
    def _on_current_note_modify(self, url: str):
        self._browser.setUrl(url)

    def _build_browser(self):
        # Set up the web view
        self._browser = QWebEngineView(self)

        # Optional: Configure settings (e.g., enable JavaScript)
        settings = self._browser.settings()
        settings.setAttribute(
            QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)

        self._spliter.addWidget(self._browser)

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

if __name__ == "__main__":
    app = QApplication(sys.argv)

    book = Book()

    main_widget = MainWidget(book)

    apply_stylesheet(
        app
        , theme='light_amber.xml'
        , css_file='style/mystyle.css'
        , invert_secondary=True
        , extra = {
            'font-family': 'Microsoft YaHei'
        }
    )
    main_widget.show()
    app.exec()
    book.save()
