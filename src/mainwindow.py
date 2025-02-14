from pathlib import Path
from PySide6.QtCore import QSettings, Slot
from PySide6.QtGui import QAction, QActionGroup, QCloseEvent, QIcon
from PySide6.QtWidgets import QHBoxLayout, QMainWindow, QSplitter, QWidget
from loguru import logger

from book import Book, Note
from browser import Browser
from notelistview import NoteListView
from resourcelistview import ResourceListView
from utils.resource import url
from nvim import Nvim
from proxy import Proxy
from utils import place_holder

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

        self.setWindowTitle("Miscellaneous")
        self.setWindowIcon(QIcon(str(Path.cwd() / 'image' / 'stack.png')))

    def _build_toolbar(self):
        self._build_main_toolbar()
        self._build_proxy_toolbar()

    def _create_action(self, icon, tips, toolbar, action_group):
        action = QAction(QIcon(url(icon)), tips, self)

        action.setCheckable(True)

        toolbar.addAction(action)
        if action_group:
            action_group.addAction(action)

        return action

    def _build_main_toolbar(self):
        toolbar = self.addToolBar('main')
        action_group = QActionGroup(self)

        toolbar.setObjectName('main')

        self._note_action = self._create_action(
            'note_stack.svg', 'Note', toolbar, action_group)

        self._dictionary_action = self._create_action(
            'dictionary.svg', 'Dictionary', toolbar, action_group)

        self._photo_action = self._create_action(
            'photo_library.svg', 'Photo', toolbar, action_group)

        self._movie_action = self._create_action(
            'movie.svg', 'Movie', toolbar, action_group)

        self._book_action = self._create_action(
            'book_5.svg', 'Book', toolbar, action_group)

        self._study_action = self._create_action(
            'school.svg', 'Study', toolbar, action_group)

        self._note_action.setChecked(True)

    def _build_proxy_toolbar(self):
        toolbar = self.addToolBar('proxy')

        toolbar.setObjectName('proxy')

        self._gpt_proxy_action = QAction(QIcon(url('chat.svg'))
                                         , 'toggle chatgpt', self)

        self._fast_proxy_action = QAction(QIcon(url('cloud_upload.svg'))
                                         , 'toggle fast proxy', self)

        self._proxy_off_action = QAction(QIcon(url('wifi_off.svg')), 
                                         'close the proxy', self)

        action_group = QActionGroup(self)

        action_group.addAction(self._gpt_proxy_action)
        action_group.addAction(self._fast_proxy_action)

        self._gpt_proxy_action.setCheckable(True)
        self._fast_proxy_action.setCheckable(True)
        self._proxy_off_action.setCheckable(True)

        self._gpt_proxy_action.setChecked(True)

        self._gpt_proxy_action.toggled.connect(self._on_gpt_proxy_toggle)
        self._fast_proxy_action.toggled.connect(self._on_fast_proxy_toggle)
        self._proxy_off_action.toggled.connect(self._on_proxy_off_toggle)

        toolbar.addWidget(place_holder())
        toolbar.addAction(self._gpt_proxy_action)
        toolbar.addAction(self._fast_proxy_action)
        toolbar.addAction(self._proxy_off_action)

        toolbar.setMovable(False)

    @Slot() #type: ignore
    def _on_proxy_off_toggle(self, checked):
        if checked:
            self._proxy.toggle_usa(False)
            self._proxy.toggle_hongkong(False)
        else:
            if self._gpt_proxy_action.isChecked():
                self._proxy.toggle_usa(True)
            else:
                self._proxy.toggle_hongkong(True)

    @Slot() #type: ignore
    def _on_gpt_proxy_toggle(self, checked):
        self._proxy.toggle_usa(checked)

    @Slot() #type: ignore
    def _on_fast_proxy_toggle(self, checked):
        self._proxy.toggle_hongkong(checked)

    @Slot() #type: ignore
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

