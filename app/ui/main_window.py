from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction  # Change this import
from PyQt6.QtWidgets import (
    QVBoxLayout,
    QWidget,
    QMainWindow,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QHeaderView,
    QMenuBar,
    QMessageBox,
    QTableWidgetItem,
    QApplication,
    QHBoxLayout,
    QMenu,
    QLabel,
)

from app.ui.about_dialog import AboutDialog
from app.ui.actions_tab import ActionsTab
from app.ui.duplicate_password_dialog import DuplicatePasswordsDialog
from app.ui.edit_password_dialog import EditPassword
from app.ui.new_entry_dialog import NewEntryDialog
from app.ui.password_generator_dialog import PasswordGenerationDialog
from app.ui.password_strength_checker_dialog import PasswordStrengthCheckerDialog
from app.ui.reset_password_dialog import ResetPasswordDialog
from app.ui.user_guide_dialog import UserGuideDialog
from app.utils.actions import Actions
from app.utils.database_manager import DatabaseManager
from app.utils.master_login import MasterLogin
from app.utils.observer import DatabaseObserver, DatabaseEvent


class PasswordManager(QMainWindow, DatabaseObserver):
    def __init__(self, db_manager=None):
        super().__init__()
        self.db_manager = db_manager if db_manager else DatabaseManager()
        self.actions = Actions(self, self.db_manager)
        self.setup_main_window()
        self.setup_menu_bar()
        self.db_manager.attach(self)  # Register as observer
        
        # Add status bar (keep only this line)
        self.status_bar = self.statusBar()
        self.setup_strength_indicator()

    def initialize_ui(self):
        self.setWindowTitle("PyQt Password Manager")
        self.setFixedSize(2000, 2000)
        self.setup_main_window()

    def setup_main_window(self):
        self.setup_menu_bar()

        main_layout = QVBoxLayout()
        main_layout.addLayout(self.create_top_bar())
        main_layout.addWidget(self.create_table_section())
        self.update_table_with_entries()
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    # Set up the menu bar with file and edit menus and their actions
    def setup_menu_bar(self):
        menubar = QMenuBar(self)
        self.setMenuBar(menubar)

        # File menu
        file_menu = menubar.addMenu("File")
        file_menu.addAction(self.actions.import_passwords_action)
        file_menu.addAction(self.actions.export_passwords_action)
        file_menu.addSeparator()
        file_menu.addAction(self.actions.backup_database_action)
        file_menu.addAction(self.actions.restore_database_action)
        file_menu.addSeparator()
        file_menu.addAction(self.actions.exit_action)

        # View menu
        view_menu = menubar.addMenu("View")
        view_menu.addAction(self.actions.show_hide_passwords_action)
        view_menu.addAction(self.actions.refresh_action)

        view_sort_sub_menu = QMenu("Sort", self)
        view_menu.addMenu(view_sort_sub_menu)
        view_sort_sub_menu.addAction(self.actions.sort_by_username_action)
        view_sort_sub_menu.addAction(self.actions.sort_by_url_action)

        # Tools menu
        tool_menu = menubar.addMenu("Tools")
        tool_menu.addAction(self.actions.password_strength_check_action)
        tool_menu.addAction(self.actions.duplicate_password_finder_action)
        tool_menu.addAction(self.actions.generate_password_action)

        # Settings menu
        settings_menu = menubar.addMenu("Settings")
        settings_menu.addAction(self.actions.encryption_settings_action)  # Add this line
        settings_menu.addAction(self.actions.password_reset_action)
        settings_menu.addAction(self.actions.user_guide_action)
        settings_menu.addAction(self.actions.about_action)

    # Create the section for searching the database and generating new passwords
    def create_top_bar(self):
        layout = QHBoxLayout()

        self.search_input = QLineEdit("Search for a specific login or username")
        self.search_input.textChanged.connect(self.filter_passwords)
        self.create_new_entry_button = QPushButton("+")
        self.create_new_entry_button.clicked.connect(self.on_new_entry_clicked)

        layout.addWidget(self.search_input)
        layout.addWidget(self.create_new_entry_button)

        return layout

    # Create the section for displaying saved password entries in a table
    def create_table_section(self):
        self.entry_table = QTableWidget()
        self.entry_table.setColumnCount(4)
        self.entry_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.entry_table.setHorizontalHeaderLabels(
            ["Website", "Username/Email", "Password", "Actions"]
        )
        self.entry_table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self.entry_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.entry_table.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        # double click
        self.entry_table.itemDoubleClicked.connect(self.on_double_click)

        return self.entry_table

    """ Table Management Methods """

    def filter_passwords(self):
        search_text = self.search_input.text().lower()
        for row in range(self.entry_table.rowCount()):
            match = False
            for column in range(self.entry_table.columnCount()):
                item = self.entry_table.item(row, column)
                if item and search_text in item.text().lower():
                    match = True
                    break
            self.entry_table.setRowHidden(row, not match)

    def update_table_with_entries(self, entries=None):
        if entries is None:
            entries = self.db_manager.load_table()

        self.entry_table.setRowCount(0)
        self.entry_table.setRowCount(len(entries))
        self.id_map = {}

        is_visible = self.actions.show_hide_passwords_action.isChecked()

        for row, entry in enumerate(entries):
            self.id_map[row] = entry["id"]
            self.entry_table.setItem(row, 0, QTableWidgetItem(entry["website"]))
            self.entry_table.setItem(row, 1, QTableWidgetItem(entry["username"]))

            if is_visible:
                self.entry_table.setItem(row, 2, QTableWidgetItem(entry["password"]))
            else:
                self.entry_table.setItem(
                    row, 2, QTableWidgetItem("*" * len(entry["password"]))
                )

            actions_tab = ActionsTab(row)
            actions_tab.view_clicked.connect(self.on_view_clicked)
            actions_tab.edit_clicked.connect(self.on_edit_clicked)
            actions_tab.delete_clicked.connect(self.on_delete_clicked)

            self.entry_table.setCellWidget(row, 3, actions_tab)

    def toggle_password_visibility(self, checked=None):
        is_visible = checked if checked is not None else self.actions.show_hide_passwords_action.isChecked()

        if is_visible:
            self.actions.show_hide_passwords_action.setText("Hide Passwords")
        else:
            self.actions.show_hide_passwords_action.setText("Show Passwords")

        for row in range(self.entry_table.rowCount()):
            password_item = self.entry_table.item(row, 2)
            if password_item:
                password_id = self.id_map.get(row)
                if password_id is not None:
                    if is_visible:
                        actual_password = self.db_manager.get_password(password_id)
                        password_item.setText(actual_password)
                    else:
                        password_item.setText("*" * len(password_item.text()))

    def sort_by_website(self):
        sorted_entries = self.db_manager.sort_by_website()
        self.update_table_with_entries(sorted_entries)

    def sort_by_username(self):
        sorted_entries = self.db_manager.sort_by_username()
        self.update_table_with_entries(sorted_entries)

    """ Entry Management Methods """

    def on_new_entry_clicked(self):
        dialog = NewEntryDialog(self)
        if dialog.exec():
            self.update_table_with_entries()

    # Open a dialog to edit an existing password entry.
    def on_edit_clicked(self, row):
        db_id = self.id_map[row]
        dialog = EditPassword(db_id, self)  # Pass self as parent
        if dialog.exec():
            self.update_table_with_entries()

    # Delete a password entry after user confirmation.
    def on_delete_clicked(self, row):
        db_id = self.id_map[row]
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            "Are you sure you want to delete this entry?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            if self.db_manager.delete_login(db_id):
                self.update_table_with_entries()  # Changed from update_table
                QMessageBox.information(self, "Success", "Entry deleted successfully.")
            else:
                QMessageBox.warning(self, "Error", "Failed to delete entry.")

    # Display the password in plain text temporarily when view action is clicked.
    def on_view_clicked(self, row):
        db_id = self.id_map[row]
        password = self.db_manager.get_password(db_id)
        if password:
            self.entry_table.setItem(row, 2, QTableWidgetItem(password))
            QTimer.singleShot(5000, lambda r=row: self.mask_password(r))

            # QMessageBox.information(self, "View Password", f"Password: {password}")
        else:
            QMessageBox.warning(self, "Error", "Failed to retrieve password.")

    # Mask the displayed password after a delay.
    def mask_password(self, row):
        item = self.entry_table.item(row, 2)
        if item:
            item.setText("*" * 12)

    # Copy the unencrypted password to clipboard on double-click.
    def on_double_click(self, item):
        db_id = self.id_map.get(item.row())

        if db_id is not None:
            unencrypted_password = self.db_manager.get_password(db_id)

            clipboard = QApplication.clipboard()
            clipboard.clear(mode=clipboard.Mode.Clipboard)
            clipboard.setText(unencrypted_password, mode=clipboard.Mode.Clipboard)

    """ Dialog Methods"""

    def show_duplicate_passwords(self):
        duplicates = self.db_manager.find_duplicate_passwords()
        if duplicates:
            dialog = DuplicatePasswordsDialog(duplicates)
            dialog.exec()
        else:
            QMessageBox.information(
                self, "No Duplicates", "No duplicate passwords found."
            )

    
    def show_about_dialog(self):
        dialog = AboutDialog(self)
        dialog.exec()

    def show_user_guide(self):
        dialog = UserGuideDialog(self)
        dialog.exec()

    # Open password generator dialog
    def open_password_generator(self):
        dialog = PasswordGenerationDialog(self, self.db_manager)
        dialog.exec()

    # Open dialog for master password reset
    def on_open_password_reset_clicked(self):
        # Create MasterLogin instance with the current db_manager
        master_login = MasterLogin()
        master_login.set_db_manager(self.db_manager)  # Set the existing db_manager
        dialog = ResetPasswordDialog(master_login, self)
        
        if dialog.exec():
            # Refresh the table after successful password reset
            self.update_table_with_entries()

    def show_password_strength_checker(self):
        dialog = PasswordStrengthCheckerDialog(self)
        dialog.exec()

    def show_encryption_settings(self):
        """Show the encryption settings dialog"""
        from app.ui.encryption_settings_dialog import EncryptionSettingsDialog
        dialog = EncryptionSettingsDialog(self, self.db_manager)
        if dialog.exec():
            self.update_table_with_entries()

    def setup_strength_indicator(self):
        """Setup the strength indicator in status bar"""
        self.strength_indicator = QLabel()
        self.status_bar.addPermanentWidget(self.strength_indicator)

    def update_strength_indicator(self, strength: str):
        """Update the password strength indicator"""
        color_map = {
            "Very Weak": "red",
            "Weak": "orange",
            "Medium": "yellow",
            "Strong": "lightgreen",
            "Very Strong": "green"
        }
        color = color_map.get(strength, "black")
        self.strength_indicator.setText(f"Password Strength: {strength}")
        self.strength_indicator.setStyleSheet(f"color: {color}; font-weight: bold;")

    def update_encryption_indicator(self, strategy: str):
        """Update the encryption strategy indicator"""
        self.status_bar.showMessage(f"Encryption: {strategy}", 3000)

    def show_status_message(self, message: str, timeout: int = 3000):
        """Show a message in the status bar"""
        self.status_bar.showMessage(message, timeout)

    def update(self, event: DatabaseEvent, data: dict) -> None:
        """Handle database change notifications"""
        match event:
            case DatabaseEvent.ENTRY_ADDED:
                self.update_table_with_entries()
                self.show_status_message("New entry added")
                
            case DatabaseEvent.ENTRY_MODIFIED:
                self.update_table_with_entries()
                self.show_status_message("Entry modified")
                
            case DatabaseEvent.ENTRY_DELETED:
                self.update_table_with_entries()
                self.show_status_message("Entry deleted")
                
            case DatabaseEvent.DATABASE_ENCRYPTED:
                self.update_table_with_entries()
                if data.get("success", False):
                    self.show_status_message("Database encryption changed successfully")
                else:
                    self.show_status_message(f"Encryption error: {data.get('error', 'Unknown error')}")
                
            case DatabaseEvent.ENCRYPTION_STRATEGY_CHANGED:
                self.update_encryption_indicator(data.get("strategy"))
                self.show_status_message(f"Encryption strategy changed to: {data.get('strategy')}")

    def closeEvent(self, event):
        """Clean up observer when window closes"""
        self.db_manager.detach(self)
        super().closeEvent(event)
