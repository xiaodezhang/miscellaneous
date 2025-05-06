from pathlib import Path
from PySide6.QtCore import QSettings, QTimer, Slot
from PySide6.QtGui import QAction, QActionGroup, QCloseEvent, QIcon
from PySide6.QtWidgets import QMainWindow, QStackedWidget

from book import Book
from noteview import NoteView
from utils.resource import url
from nvim import Nvim
from proxy import Proxy
from utils import place_holder

class MainWindow(QMainWindow):
    # def __init__(self, book: Book, nvim: Nvim, proxy: Proxy, graph: Graph):
    def __init__(self, book: Book, nvim: Nvim, proxy: Proxy):
        super().__init__()

        self._proxy = proxy
        # self._graph = graph
        self._book = book

        container = QStackedWidget()
        self._note_view = NoteView(book, nvim)

        container.addWidget(self._note_view)
        self.setCentralWidget(container)

        self._build_toolbar()

        self.resize(1200, 800)

        self._read_settings()

        # graph.modified.connect(self._on_graph_modify)

        self.setWindowTitle("Miscellaneous")
        self.setWindowIcon(QIcon(str(Path.cwd() / 'image' / 'stacks.png')))

    # @Slot()
    # def _on_graph_modify(self):
    #     note = self._book.current_note
    #     if note:
    #         file_name = note.html_folder / 'test.xml'
    #         with open(file_name, 'w') as file:
    #             file.write(self._graph.ink)
    #
    #         QTimer.singleShot(300, lambda: self._note_view.reload())

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

    def closeEvent(self, event: QCloseEvent) -> None:
        settings = QSettings("duduhome", 'note')
        settings.setValue("geometry", self.saveGeometry())
        settings.setValue("windowState", self.saveState())

        return super().closeEvent(event)

    def _read_settings(self):
        settings = QSettings("duduhome", 'note')
        self.restoreGeometry(settings.value("geometry")) #type: ignore
        self.restoreState(settings.value("windowState")) #type: ignore

