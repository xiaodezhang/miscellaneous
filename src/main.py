import sys
from PySide6.QtWidgets import QApplication
from platformdirs import user_data_path
from qt_material import apply_stylesheet

from book import Book
from mainwindow import MainWindow
from nvim import Nvim
from proxy import Proxy

if __name__ == "__main__":

    path = user_data_path() / 'miscellaneous' / '.htmls'
    # server = subprocess.Popen(['python', '-m', 'http.server', '8000', '--directory', f'{path}'])

    app = QApplication(sys.argv)

    book = Book()

    nvim = Nvim()

    proxy = Proxy()

    # graph = Graph()
    #
    # graph.start()

    main_widget = MainWindow(book, nvim, proxy)

    apply_stylesheet(
        app
        , theme='light_amber.xml'
        , css_file='style/mystyle.css'
        , invert_secondary=True
    )

    main_widget.show()
    app.exec()
    book.save()
    nvim.close()
    proxy.close()
    # os.kill(server.pid, signal.SIGTERM)
    # graph.stop()
    # graph.quit()
    # graph.wait()
