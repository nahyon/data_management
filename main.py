from PySide6.QtWidgets import QApplication

from main_menu.main_menu import MainMenu

if __name__ == '__main__':
    app = QApplication()
    window = MainMenu()
    window.show()
    app.exec()
