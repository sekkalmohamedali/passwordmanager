import os
import sys
from PyQt6.QtWidgets import QApplication, QMessageBox
from app.ui.login_dialog import LoginDialog
from app.ui.create_password_dialog import CreatePasswordDialog
from app.ui.main_window import PasswordManager
from app.utils.database_manager import DatabaseManager
from app.utils.master_login import MasterLogin


def main():
    app = QApplication(sys.argv)
    
    try:
        db_manager = DatabaseManager()
        password_manager = MasterLogin()
        password_manager.set_db_manager(db_manager)

        if not password_manager.password_exists():
            create_dialog = CreatePasswordDialog(password_manager)
            if create_dialog.exec():
                show_main_window(app, db_manager)
            else:
                sys.exit()
        else:
            login_dialog = LoginDialog(password_manager)
            if login_dialog.exec():
                show_main_window(app, db_manager)
            else:
                sys.exit()
    except Exception as e:
        QMessageBox.critical(None, "Error", f"Failed to initialize application: {str(e)}")
        sys.exit(1)


def show_main_window(app, db_manager):
    main_window = PasswordManager(db_manager)  # Now correctly passes db_manager
    main_window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
