from PySide6.QtCore import QSettings, Slot
from PySide6.QtGui import QAction, QCloseEvent, QIcon
from PySide6.QtWidgets import QHBoxLayout, QMainWindow, QSplitter, QWidget
from loguru import logger

from book import Book, Note
from browser import Browser
from notelistview import NoteListView
from resourcelistview import ResourceListView
from utils.resource import url
from nvim import Nvim
from proxy import Proxy

class MainWindow(QMainWindow):
    def __init__(self, book: Book, nvim: Nvim, proxy: Proxy):
        super().__init__()

        self._nvim = nvim
        self._proxy = proxy

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
        self._build_toolbar()

        book.current_note_modified.connect(self._on_current_note_modify)
        book.current_note_changed.connect(lambda note: self._switch_note(note))
        book.new_note.connect(lambda note: self._switch_note(note))

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
            self._switch_note(book.current_note)

        self._spliter.setSizes([330, 1200, 300])
        self.resize(1200, 800)

        self._read_settings()

        self.setWindowTitle("Note")
        self.setWindowIcon(QIcon(url('note_stack.svg')))

    def _build_toolbar(self):
        toolbar = self.addToolBar('')

        self._gpt_proxy_action = QAction(QIcon(url('chat.svg'))
                                         , 'toggle chatgpt', self)

        self._fast_proxy_action = QAction(QIcon(url('cloud_upload.svg'))
                                         , 'toggle fast proxy', self)

        self._gpt_proxy_action.setCheckable(True)
        self._fast_proxy_action.setCheckable(True)
        self._gpt_proxy_action.setChecked(True)

        self._gpt_proxy_action.toggled.connect(self._on_gpt_proxy_toggle)
        self._fast_proxy_action.toggled.connect(self._on_fast_proxy_toggle)

        toolbar.addAction(self._gpt_proxy_action)
        toolbar.addAction(self._fast_proxy_action)

        toolbar.setMovable(False)

    @Slot()
    def _on_gpt_proxy_toggle(self, checked):
        if self._proxy.usa_opened == checked:
            return
        self._proxy.toggle_usa()
        self._update_proxy_status()

    @Slot()
    def _on_fast_proxy_toggle(self, checked):
        if self._proxy.hongkong_opened == checked:
            return
        self._proxy.toggle_hongkong()
        self._update_proxy_status()

    def _update_proxy_status(self):
        self._gpt_proxy_action.setChecked(self._proxy.usa_opened)
        self._fast_proxy_action.setChecked(self._proxy.hongkong_opened)

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

