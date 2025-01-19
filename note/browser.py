from PySide6.QtGui import QDragEnterEvent, QDropEvent
from PySide6.QtWebEngineCore import QWebEngineSettings
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QSizePolicy
from loguru import logger

from book import Book

class Browser(QWebEngineView):
    def __init__(self, parent, book: Book):
        super().__init__(parent)
        self._book = book

        self.setAcceptDrops(True)

        # Optional: Configure settings (e.g., enable JavaScript)
        # settings = self.settings()
        # settings.setAttribute(
        #     QWebEngineSettings.WebAttribute.PluginsEnabled, True)

    def dragEnterEvent(self, e: QDragEnterEvent) -> None:
        if e.mimeData().hasUrls():  # 判断是否是文件
            e.acceptProposedAction()  # 接受拖放事件
        return super().dragEnterEvent(e)

    def dropEvent(self, e: QDropEvent) -> None:
        urls = e.mimeData().urls()  # 获取拖放的文件路径
        if urls:
            file_path = urls[0].toLocalFile()  # 获取第一个文件的路径
            logger.debug(f"file_path: {file_path}")
            self._book.add_resource(file_path)

        return super().dropEvent(e)
