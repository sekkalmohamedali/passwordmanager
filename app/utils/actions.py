# actions.py
from PyQt6.QtGui import QIcon, QAction


class Actions:
    def __init__(self, parent_window, db_manager):
        self.parent = parent_window
        self.db_manager = db_manager
        self.setup_actions()

    def setup_actions(self):
        # File menu actions
        self.import_passwords_action = self.create_action(
            "Import Passwords", self.import_passwords
        )
        self.export_passwords_action = self.create_action(
            "Export Passwords", self.export_passwords
        )
        self.backup_database_action = self.create_action(
            "Backup Database", self.backup_database
        )
        self.restore_database_action = self.create_action(
            "Restore Database", self.restore_database
        )
        self.exit_action = self.create_action("Exit", self.parent.close)

        # View menu actions
        self.show_hide_passwords_action = self.create_action(
            "Show Passwords", self.toggle_password_visibility, checkable=True
        )
        self.refresh_action = self.create_action("Refresh", self.refresh_view)
        self.sort_by_username_action = self.create_action(
            "Sort by Username", self.sort_by_username
        )
        self.sort_by_url_action = self.create_action(
            "Sort by Website", self.sort_by_website
        )

        # Tool Actions
        self.password_strength_check_action = self.create_action(
            "Password Strength Checker", self.show_password_strength_checker
        )
        self.duplicate_password_finder_action = self.create_action(
            "Duplicate Password Finder", self.show_duplicate_passwords
        )
        self.password_history_action = self.create_action(
            "Password History", self.show_password_history
        )
        self.generate_password_action = self.create_action(
            "Generate Password", self.open_password_generator
        )

        # Settings Actions
        self.password_reset_action = self.create_action(
            "Reset Master Password", self.on_open_password_reset_clicked
        )
        self.user_guide_action = self.create_action(
            "User Guide", self.show_user_guide
        )
        self.about_action = self.create_action("About", self.show_about_dialog)

        # Add encryption settings action
        self.encryption_settings_action = QAction("Encryption Settings", self.parent)
        self.encryption_settings_action.triggered.connect(
            self.parent.show_encryption_settings
        )

        # Add access logs action
        self.view_logs_action = self.create_action(
            "View Access Logs", self.show_access_logs
        )

    def create_action(self, text, slot, checkable=False):
        action = QAction(QIcon(), text, self.parent)
        action.setStatusTip(text)
        action.triggered.connect(slot)
        action.setCheckable(checkable)
        return action

    def import_passwords(self):
        self.db_manager.import_data()

    def export_passwords(self):
        self.db_manager.export_data()

    def backup_database(self):
        self.db_manager.backup_database()

    def restore_database(self):
        self.db_manager.restore_database()

    def toggle_password_visibility(self, checked):
        self.parent.toggle_password_visibility(checked)

    def refresh_view(self):
        self.parent.update_table_with_entries()

    def sort_by_username(self):
        self.parent.sort_by_username()

    def sort_by_website(self):
        self.parent.sort_by_website()

    def show_password_strength_checker(self):
        self.parent.show_password_strength_checker()

    def show_duplicate_passwords(self):
        self.parent.show_duplicate_passwords()

    def show_password_history(self):
        self.parent.show_password_history()

    def open_password_generator(self):
        self.parent.open_password_generator()

    def on_open_password_reset_clicked(self):
        self.parent.on_open_password_reset_clicked()

    def show_user_guide(self):
        self.parent.show_user_guide()

    def show_about_dialog(self):
        self.parent.show_about_dialog()

    def show_access_logs(self):
        self.parent.show_access_logs()
