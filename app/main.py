import os
import sys
from PyQt6.QtWidgets import QApplication
from app.ui.login_dialog import LoginDialog
from app.ui.create_password_dialog import CreatePasswordDialog
from app.ui.main_window import PasswordManager
from app.utils.database_manager import DatabaseManager
from app.utils.master_login import MasterLogin


def main():
    app = QApplication(sys.argv)
    password_manager = MasterLogin()

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
    main_window = PasswordManager()
    main_window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
