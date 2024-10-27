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
    QHBoxLayout,
)

from app.ui.actions_tab import ActionsTab
from app.ui.edit_password_dialog import EditPassword
from app.ui.new_entry_dialog import NewEntryDialog
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
        file_menu.addAction(self.password_reset_action)
        file_menu.addAction(self.export_csv_action)
        file_menu.addSeparator()  # Add a separator line
        file_menu.addAction(self.exit_action)

    # Create actions for menu items such as exit and export
    def create_actions(self):
        # File actions
        self.exit_action = QAction(QIcon(), "Exit", self) # Exit
        self.exit_action.setStatusTip("Exit the application")
        self.exit_action.triggered.connect(self.close)

        self.export_csv_action = QAction(QIcon(), "Export", self) # Export to .csv
        self.export_csv_action.setStatusTip("Export password to .csv")
        self.export_csv_action.triggered.connect(self.db_manager.export_to_csv)

        self.password_reset_action = QAction(QIcon(), "Reset Master Password", self) # Password Reset
        self.password_reset_action.triggered.connect(self.on_open_password_reset_clicked)

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
