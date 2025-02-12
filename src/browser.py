from PySide6.QtCore import Signal, Slot
from PySide6.QtGui import QAction, QDragEnterEvent, QDropEvent, QIcon
from PySide6.QtWebEngineCore import QWebEngineSettings
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QMainWindow, QSizePolicy
from loguru import logger

from book import Book
from utils import append_class, place_holder
from utils.resource import url 

class DragWebEngineView(QWebEngineView):
    def __init__(self, parent, book):
        super().__init__(parent)
        self._book = book
        self.setAcceptDrops(True)

    def dragEnterEvent(self, e: QDragEnterEvent) -> None:
        if e.mimeData().hasUrls():  # 判断是否是文件
            e.acceptProposedAction()  # 接受拖放事件
        return super().dragEnterEvent(e)

    def dropEvent(self, e: QDropEvent) -> None:
        urls = e.mimeData().urls()  # 获取拖放的文件路径
        if urls:
            file_path = urls[0].toLocalFile()  # 获取第一个文件的路径
            self._book.add_resource(file_path)
        return super().dropEvent(e)

class Browser(QMainWindow):
    side_note_triggered = Signal()
    side_resource_triggered = Signal()

    def __init__(self, parent, book: Book):
        super().__init__(parent)
        self._book = book

        self._web_engine_view = DragWebEngineView(self, book)

        self._tool_bar = self.addToolBar('')

        self._tool_bar.setMovable(False)

        self._side_note_action = QAction(QIcon(url("note_stack_normal.svg")),
                                        "view note side bar", self)

        self._side_resource_action = QAction(QIcon(url("photo_library.svg")),
                                        "view resources side bar", self)

        self._tool_bar.addAction(self._side_note_action)
        self._tool_bar.addAction(self._side_resource_action)

        self._side_note_action.triggered.connect(self._on_side_note_trigger)
        self._side_resource_action.triggered.connect(self._on_side_resource_trigger)

        self.setCentralWidget(self._web_engine_view)

        self._side_note_action.setVisible(False)
        self._side_resource_action.setVisible(False)

        self._tool_bar.setStyleSheet("""
            QToolBar {
                border: none;
            }
        """)

        # Optional: Configure settings (e.g., enable JavaScript)
        # settings = self.settings()
        # settings.setAttribute(
        #     QWebEngineSettings.WebAttribute.PluginsEnabled, True)

    @Slot()
    def _on_side_note_trigger(self):
        self.side_note_triggered.emit()
        self._side_note_action.setVisible(False)

    @Slot()
    def _on_side_resource_trigger(self):
        self.side_resource_triggered.emit()
        self._side_resource_action.setVisible(False)

    def setUrl(self, url):
        self._web_engine_view.setUrl(url)

    def show_side_note_action(self):
        self._side_note_action.setVisible(True)

    def show_side_resource_action(self):
        self._side_resource_action.setVisible(True)
