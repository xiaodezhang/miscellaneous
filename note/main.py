import socket
import sys
from PySide6 import QtCore
from PySide6.QtWidgets import QApplication
from loguru import logger
from qt_material import apply_stylesheet

from book import Book
from mainwindow import MainWindow
from nvim import Nvim

if __name__ == "__main__":

    app = QApplication(sys.argv)

    book = Book()

    nvim = Nvim()

    main_widget = MainWindow(book, nvim)

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
    nvim.close()
