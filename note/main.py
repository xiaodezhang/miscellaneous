import sys
from PySide6 import QtCore
from PySide6.QtWidgets import QApplication
from loguru import logger
from qt_material import apply_stylesheet

from book import Book
from mainwindow import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)

    book = Book()

    main_widget = MainWindow(book)

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
