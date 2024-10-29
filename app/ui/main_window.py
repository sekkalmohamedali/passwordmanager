import random
import string

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import (
    QVBoxLayout,
    QWidget,
    QMainWindow,
    QFormLayout,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QHeaderView,
    QGroupBox,
    QGridLayout,
    QCheckBox,
    QLabel,
    QSlider,
    QMenuBar,
    QMessageBox,
    QTableWidgetItem,
    QApplication,
    QHBoxLayout, QMenu,
)

from app.ui.actions_tab import ActionsTab
from app.ui.duplicate_password_dialog import DuplicatePasswordsDialog
from app.ui.edit_password_dialog import EditPassword
from app.ui.new_entry_dialog import NewEntryDialog
from app.ui.password_generator_dialog import PasswordGenerationDialog
from app.ui.password_histroy_dialog import PasswordHistoryDialog
from app.ui.reset_password_dialog import ResetPasswordDialog
from app.utils.database_manager import DatabaseManager
from app.utils.master_login import MasterLogin


class PasswordManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db_manager = DatabaseManager()
        self.initialize_ui()

    # Initialize the main window UI settings such as title and size
    def initialize_ui(self):
        self.setWindowTitle("PyQt Password Manager")
        self.setFixedSize(800, 600)
        self.setup_main_window()

    # Set up the main window layout and components
    def setup_main_window(self):
        self.create_actions()
        self.setup_menu_bar()

        main_layout = QVBoxLayout()
        main_layout.addLayout(self.create_top_bar())
        main_layout.addWidget(self.create_table_section())
        self.update_table()
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

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

    # Create the section for searching the database and generating new passwords
    def create_top_bar(self):
        layout = QHBoxLayout()

        self.search_input = QLineEdit("Search for a specific login")
        self.create_new_entry_button = QPushButton("+")
        new_entry_dialog = NewEntryDialog(self)
        self.create_new_entry_button.clicked.connect(self.on_new_entry_clicked)

        layout.addWidget(self.search_input)
        layout.addWidget(self.create_new_entry_button)

        return layout

    # Set up the menu bar with file and edit menus and their actions
    def setup_menu_bar(self):
        menubar = QMenuBar(self)
        self.setMenuBar(menubar)

        # Create File menu and add actions
        file_menu = menubar.addMenu("File")
        file_menu.addAction(self.import_passwords_action)
        file_menu.addAction(self.export_passwords_action)
        file_menu.addSeparator()
        file_menu.addAction(self.backup_database_action)
        file_menu.addAction(self.restore_database_action)
        file_menu.addSeparator()
        file_menu.addAction(self.exit_action)

        # Create Edit menu and add actions
        edit_menu = menubar.addMenu("Edit")
        # Add edit actions here

        # Create View menu and add actions
        view_menu = menubar.addMenu("View")
        view_menu.addAction(self.show_hide_passwords_action)
        view_menu.addAction(self.refresh_action)

        view_sort_sub_menu = QMenu("Sort", self)
        view_menu.addMenu(view_sort_sub_menu)
        view_sort_sub_menu.addAction(self.sort_by_username_action)
        view_sort_sub_menu.addAction(self.sort_by_url_action)

        # Create Tool menu and add actions
        tool_menu = menubar.addMenu("Tools")
        tool_menu.addAction(self.password_strength_check_action)
        tool_menu.addAction(self.duplicate_password_finder_action)
        tool_menu.addAction(self.password_history_action)
        tool_menu.addAction(self.generate_password_action)

        # Create Settings menu and add actions
        settings_menu = menubar.addMenu("Settings")
        settings_menu.addAction(self.password_reset_action)
        settings_menu.addAction(self.user_guild_action)
        settings_menu.addAction(self.about_action)

    def create_actions(self):
        # File actions
        self.import_passwords_action = QAction(QIcon(), "Import", self)
        self.import_passwords_action.setStatusTip("Import passwords from a file")
        self.import_passwords_action.triggered.connect(self.db_manager.import_data)

        self.export_passwords_action = QAction(QIcon(), "Export", self)
        self.export_passwords_action.setStatusTip("Export passwords to a file")
        self.export_passwords_action.triggered.connect(self.db_manager.export_data)

        self.backup_database_action = QAction(QIcon(), "Backup", self)
        self.backup_database_action.setStatusTip("Create a backup of the database")
        self.backup_database_action.triggered.connect(self.db_manager.backup_database)

        self.restore_database_action = QAction(QIcon(), "Restore", self)
        self.restore_database_action.setStatusTip("Restore the database from a backup")
        self.restore_database_action.triggered.connect(self.db_manager.restore_database)

        self.exit_action = QAction(QIcon(), "Exit", self)
        self.exit_action.setStatusTip("Exit the application")
        self.exit_action.triggered.connect(self.close)

        # View Actions
        self.show_hide_passwords_action = QAction(QIcon(), "Show/Hide Passwords", self)
        self.show_hide_passwords_action.setStatusTip("Toggle password visibility")
        self.show_hide_passwords_action.triggered.connect(self.toggle_password_visibility)
        self.show_hide_passwords_action.setCheckable(True)

        self.refresh_action = QAction(QIcon(), "Refresh", self)
        self.refresh_action.setStatusTip("Refresh the password list")
        self.refresh_action.triggered.connect(self.update_table)

        # Sort Actions
        self.sort_by_username_action = QAction(QIcon(), "Sort by Username", self)
        self.sort_by_username_action.setStatusTip("Sort the list by username")
        self.sort_by_username_action.triggered.connect(self.sort_by_username)

        self.sort_by_url_action = QAction(QIcon(), "Sort by Website", self)
        self.sort_by_url_action.setStatusTip("Sort the list by website")
        self.sort_by_url_action.triggered.connect(self.sort_by_website)

        # Tool Actions
        self.password_strength_check_action = QAction(QIcon(), "Password Strength Checker", self)
        self.password_strength_check_action.setStatusTip("Check the strength of your passwords")

        self.duplicate_password_finder_action = QAction(QIcon(), "Duplicate Password Finder", self)
        self.duplicate_password_finder_action.setStatusTip("Find duplicate passwords in your list")
        self.duplicate_password_finder_action.triggered.connect(self.show_duplicate_passwords)

        self.password_history_action = QAction(QIcon(), "Password History", self)
        self.password_history_action.setStatusTip("View password change history")
        self.password_history_action.triggered.connect(self.show_password_history)

        self.generate_password_action = QAction(QIcon(), "Generate Password", self)
        self.generate_password_action.setStatusTip("Open Password Generator")
        self.generate_password_action.triggered.connect(self.open_password_generator)

        # Settings Actions
        self.password_reset_action = QAction(QIcon(), "Reset Master Password", self)
        self.password_reset_action.setStatusTip("Change your master password")
        self.password_reset_action.triggered.connect(self.on_open_password_reset_clicked)

        self.user_guild_action = QAction(QIcon(), "User Guide", self)
        self.user_guild_action.setStatusTip("View the user guide")

        self.about_action = QAction(QIcon(), "About", self)
        self.about_action.setStatusTip("Show information about the application")

    def sort_by_website(self):
        sorted_entries = self.db_manager.sort_by_website()
        self.update_table_with_entries(sorted_entries)

    def sort_by_username(self):
        sorted_entries = self.db_manager.sort_by_username()
        self.update_table_with_entries(sorted_entries)

    def update_table_with_entries(self, entries):
        self.entry_table.setRowCount(0)
        self.entry_table.setRowCount(len(entries))
        self.id_map.clear()

        is_visible = self.show_hide_passwords_action.isChecked()

        for row, entry in enumerate(entries):
            self.id_map[row] = entry["id"]
            self.entry_table.setItem(row, 0, QTableWidgetItem(entry["website"]))
            self.entry_table.setItem(row, 1, QTableWidgetItem(entry["username"]))

            if is_visible:
                self.entry_table.setItem(row, 2, QTableWidgetItem(entry["password"]))
            else:
                self.entry_table.setItem(row, 2, QTableWidgetItem("*" * len(entry["password"])))

            actions_tab = ActionsTab(row)
            actions_tab.view_clicked.connect(self.on_view_clicked)
            actions_tab.edit_clicked.connect(self.on_edit_clicked)
            actions_tab.delete_clicked.connect(self.on_delete_clicked)

            self.entry_table.setCellWidget(row, 3, actions_tab)

    def toggle_password_visibility(self):
        is_visible = self.show_hide_passwords_action.isChecked()

        if is_visible:
            self.show_hide_passwords_action.setText("Hide Passwords")
        else:
            self.show_hide_passwords_action.setText("Show Passwords")

        for row in range(self.entry_table.rowCount()):
            password_item = self.entry_table.item(row, 2)
            if password_item:
                password_id = self.id_map.get(row)
                if password_id is not None:
                    if is_visible:
                        # Fetch and show the actual password
                        actual_password = self.db_manager.get_password(password_id)
                        password_item.setText(actual_password)
                    else:
                        # Hide the password
                        password_item.setText('*' * len(password_item.text()))

    def show_duplicate_passwords(self):
        duplicates = self.db_manager.find_duplicate_passwords()
        if duplicates:
            dialog = DuplicatePasswordsDialog(duplicates)
            dialog.exec()
        else:
            QMessageBox.information(self, "No Duplicates", "No duplicate passwords found.")

    def show_password_history(self):
            current_row = self.entry_table.currentRow()
            if current_row >= 0:
                login_id = self.id_map[current_row]
                passwords = self.db_manager.get_password_history(login_id)

                if passwords:
                    dialog = PasswordHistoryDialog(passwords)
                    dialog.exec()
                else:
                    QMessageBox.information(self, "No History", "No password history available for this entry.")
            else:
                QMessageBox.warning(self, "No Selection", "Please select an entry to view its password history.")

    """ Actions Tab """

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

    # Open a dialog to edit an existing password entry.
    def on_edit_clicked(self, row):
        db_id = self.id_map[row]
        EditPassword(db_id).exec()

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
                self.update_table()
                QMessageBox.information(self, "Success", "Entry deleted successfully.")
            else:
                QMessageBox.warning(self, "Error", "Failed to delete entry.")

    # Copy the unencrypted password to clipboard on double-click.
    def on_double_click(self, item):
        db_id = self.id_map.get(item.row())

        if db_id is not None:
            unencrypted_password = self.db_manager.get_password(db_id)

            clipboard = QApplication.clipboard()
            clipboard.clear(mode=clipboard.Mode.Clipboard)
            clipboard.setText(unencrypted_password, mode=clipboard.Mode.Clipboard)

    """ Generic Functions"""

    # Open password generator dialog
    def open_password_generator(self):
        dialog = PasswordGenerationDialog(self)
        dialog.exec()
    # Open dialog for master password reset
    def on_open_password_reset_clicked(self):
        master_login = MasterLogin()
        dialog = ResetPasswordDialog(master_login, self)
        dialog.exec()

    # Open dialog for master password reset
    def on_new_entry_clicked(self):
        dialog = NewEntryDialog(self)
        dialog.exec()

    # Update the table view with entries from the database.
    def update_table(self):
            entries = self.db_manager.load_table()
            self.entry_table.setRowCount(len(entries))
            self.id_map = {}  # Dictionary to map row numbers to database IDs
            for row, entry in enumerate(entries):
                self.id_map[row] = entry["id"]
                self.entry_table.setItem(row, 0, QTableWidgetItem(entry["website"]))
                self.entry_table.setItem(row, 1, QTableWidgetItem(entry["username"]))
                self.entry_table.setItem(
                    row, 2, QTableWidgetItem("*" * len(entry["password"]))
                )

                actions_tab = ActionsTab(row)
                actions_tab.view_clicked.connect(self.on_view_clicked)
                actions_tab.edit_clicked.connect(self.on_edit_clicked)
                actions_tab.delete_clicked.connect(self.on_delete_clicked)

                self.entry_table.setCellWidget(row, 3, actions_tab)
