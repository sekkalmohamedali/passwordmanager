import sys
from PyQt6.QtWidgets import QApplication
from src.ui.login_dialog import LoginDialog
from src.ui.create_password_dialog import CreatePasswordDialog
from src.ui.main_window import MainWindow
from src.utils.password_settings import PasswordManager

def main():
    app = QApplication(sys.argv)
    password_manager = PasswordManager()

    if not password_manager.password_exists():
        create_dialog = CreatePasswordDialog(password_manager)
        if create_dialog.exec():
            show_main_window(app)
        else:
            sys.exit()
    else:
        login_dialog = LoginDialog(password_manager)
        if login_dialog.exec():
            show_main_window(app)
        else:
            sys.exit()

def show_main_window(app):
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()