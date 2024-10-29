# actions.py
from PyQt6.QtGui import QIcon, QAction


class Actions:
    def __init__(self, main_window):
        self.main_window = main_window
        self.db_manager = main_window.db_manager
        self.create_actions()

    def create_actions(self):
        # File actions
        self.import_passwords_action = QAction(QIcon(), "Import", self.main_window)
        self.import_passwords_action.setStatusTip("Import passwords from a file")
        self.import_passwords_action.triggered.connect(self.db_manager.import_data)

        self.export_passwords_action = QAction(QIcon(), "Export", self.main_window)
        self.export_passwords_action.setStatusTip("Export passwords to a file")
        self.export_passwords_action.triggered.connect(self.db_manager.export_data)

        self.backup_database_action = QAction(QIcon(), "Backup", self.main_window)
        self.backup_database_action.setStatusTip("Create a backup of the database")
        self.backup_database_action.triggered.connect(self.db_manager.backup_database)

        self.restore_database_action = QAction(QIcon(), "Restore", self.main_window)
        self.restore_database_action.setStatusTip("Restore the database from a backup")
        self.restore_database_action.triggered.connect(self.db_manager.restore_database)

        self.exit_action = QAction(QIcon(), "Exit", self.main_window)
        self.exit_action.setStatusTip("Exit the application")
        self.exit_action.triggered.connect(self.main_window.close)

        # View Actions
        self.show_hide_passwords_action = QAction(
            QIcon(), "Show/Hide Passwords", self.main_window
        )
        self.show_hide_passwords_action.setStatusTip("Toggle password visibility")
        self.show_hide_passwords_action.triggered.connect(
            self.main_window.toggle_password_visibility
        )
        self.show_hide_passwords_action.setCheckable(True)

        self.refresh_action = QAction(QIcon(), "Refresh", self.main_window)
        self.refresh_action.setStatusTip("Refresh the password list")
        self.refresh_action.triggered.connect(
            self.main_window.update_table_with_entries
        )

        # Sort Actions
        self.sort_by_username_action = QAction(
            QIcon(), "Sort by Username", self.main_window
        )
        self.sort_by_username_action.setStatusTip("Sort the list by username")
        self.sort_by_username_action.triggered.connect(
            self.main_window.sort_by_username
        )

        self.sort_by_url_action = QAction(QIcon(), "Sort by Website", self.main_window)
        self.sort_by_url_action.setStatusTip("Sort the list by website")
        self.sort_by_url_action.triggered.connect(self.main_window.sort_by_website)

        # Tool Actions
        self.password_strength_check_action = QAction(
            QIcon(), "Password Strength Checker", self.main_window
        )
        self.password_strength_check_action.setStatusTip(
            "Check the strength of your passwords"
        )

        self.duplicate_password_finder_action = QAction(
            QIcon(), "Duplicate Password Finder", self.main_window
        )
        self.duplicate_password_finder_action.setStatusTip(
            "Find duplicate passwords in your list"
        )
        self.duplicate_password_finder_action.triggered.connect(
            self.main_window.show_duplicate_passwords
        )

        self.password_history_action = QAction(
            QIcon(), "Password History", self.main_window
        )
        self.password_history_action.setStatusTip("View password change history")
        self.password_history_action.triggered.connect(
            self.main_window.show_password_history
        )

        self.generate_password_action = QAction(
            QIcon(), "Generate Password", self.main_window
        )
        self.generate_password_action.setStatusTip("Open Password Generator")
        self.generate_password_action.triggered.connect(
            self.main_window.open_password_generator
        )

        # Settings Actions
        self.password_reset_action = QAction(
            QIcon(), "Reset Master Password", self.main_window
        )
        self.password_reset_action.setStatusTip("Change your master password")
        self.password_reset_action.triggered.connect(
            self.main_window.on_open_password_reset_clicked
        )

        self.user_guide_action = QAction(QIcon(), "User Guide", self.main_window)
        self.user_guide_action.setStatusTip("View the user guide")
        self.user_guide_action.triggered.connect(self.main_window.show_user_guide)

        self.about_action = QAction(QIcon(), "About", self.main_window)
        self.about_action.setStatusTip("Show information about the application")
        self.about_action.triggered.connect(self.main_window.show_about_dialog)
