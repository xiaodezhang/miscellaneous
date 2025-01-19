from PySide6.QtWidgets import QApplication
from qt_material import apply_stylesheet

if __name__ == "__main__":
    app = QApplication()
    apply_stylesheet(app, theme='dark_yellow.xml', css_file='style/mystyle.css')
    with open('style/material_style.css', 'w') as file:
        file.write(app.styleSheet())
