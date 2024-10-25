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
        main_layout.addLayout(self.create_entry_section())
        main_layout.addWidget(self.create_table_section())
        main_layout.addWidget(self.create_password_generation_section())
        self.update_table()
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    # Create the section for entering new password entries
    def create_entry_section(self):
        form_layout = QFormLayout()
        self.entry_url = QLineEdit()
        self.entry_username = QLineEdit()
        self.entry_password = QLineEdit()
        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.entry_save_btn = QPushButton("Save")
        self.entry_save_btn.setFixedWidth(250)
        btn_layout.addWidget(self.entry_save_btn)

        form_layout.addRow("Website/URL:", self.entry_url)
        form_layout.addRow("Username/Email:", self.entry_username)
        form_layout.addRow("Password:", self.entry_password)
        form_layout.addRow(btn_layout)

        self.entry_save_btn.clicked.connect(self.save_new_entry)

        return form_layout

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

    # Create the section for generating passwords with various options
    def create_password_generation_section(self):
        group_box = QGroupBox("Password Generation")
        layout = QGridLayout()
        group_box.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Password field and generate button
        self.password_field = QLineEdit()
        self.password_field.setPlaceholderText("Generated password will appear here")
        self.password_field.setReadOnly(True)

        self.generate_password_btn = QPushButton("Generate Password")
        self.generate_password_btn.clicked.connect(self.generate_password)

        # Character options
        self.alpha_char = QCheckBox("Include Capital Letters (A-Z)")
        self.numerical_char = QCheckBox("Include Numbers (0-9)")
        self.special_char = QCheckBox("Include Special Characters (!@#$%^*)")

        # Password length slider
        self.char_length = QSlider(Qt.Orientation.Horizontal)
        self.char_length.setRange(12, 75)
        self.char_length.setValue(12)  # Set default value
        self.char_length_label = QLabel("Password Length: 12")
        self.char_length.valueChanged.connect(self.update_password_length)

        # Integrating generated password
        self.integrate_password = QCheckBox("Use for New Entry")

        # Layout
        layout.addWidget(self.password_field, 0, 0, 1, 2)
        layout.addWidget(self.generate_password_btn, 0, 2)
        layout.addWidget(self.integrate_password, 0, 3, Qt.AlignmentFlag.AlignLeft)

        layout.addWidget(self.alpha_char, 1, 0, 1, 1, Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.numerical_char, 2, 0, 1, 1, Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.special_char, 3, 0, 1, 1, Qt.AlignmentFlag.AlignLeft)

        layout.addWidget(self.char_length, 1, 1, 2, 3)
        layout.addWidget(
            self.char_length_label, 3, 1, 1, 3, Qt.AlignmentFlag.AlignCenter
        )

        group_box.setLayout(layout)
        return group_box

    # Set up the menu bar with file and edit menus and their actions
    def setup_menu_bar(self):
        menubar = QMenuBar(self)
        self.setMenuBar(menubar)

        # Create File menu and add actions
        file_menu = menubar.addMenu("File")
        file_menu.addAction(self.password_reset)
        file_menu.addAction(self.export_csv_action)
        file_menu.addSeparator()  # Add a separator line
        file_menu.addAction(self.minimize_action)
        file_menu.addAction(self.exit_action)

        # Create Edit menu and add actions
        edit_menu = menubar.addMenu("Edit")

    # Create actions for menu items such as exit and export
    def create_actions(self):
        # File actions

        # Exit
        self.exit_action = QAction(QIcon(), "Exit", self)
        self.exit_action.setStatusTip("Exit the application")
        self.exit_action.triggered.connect(self.close)
        # Minimize
        self.minimize_action = QAction(QIcon(), "Minimize", self)
        self.minimize_action.setStatusTip("Minimize the application")
        self.minimize_action.triggered.connect(self.showMinimized)

        # Export to .csv
        self.export_csv_action = QAction(QIcon(), "Export", self)
        self.export_csv_action.setStatusTip("Export password to .csv")
        self.export_csv_action.triggered.connect(self.db_manager.export_to_csv)

        # Settings
        self.password_reset = QAction(QIcon(),"Reset Master Password",self)
        self.password_reset.triggered.connect(self.open_reset_password_dialog)
    # Open dialog for master password reset
    def open_reset_password_dialog(self):
        master_login = MasterLogin()
        dialog = ResetPasswordDialog(master_login, self)
        dialog.exec()

    """ Actions Tab """

    # Save a new password entry to the database and update the table view
    def save_new_entry(self):
        url = self.entry_url.text().strip()
        username = self.entry_username.text().strip()
        password = self.entry_password.text().strip()

        if not url or not username or not password:
            QMessageBox.warning(
                self,
                "Incomplete Entry",
                "Please fill in all fields (URL, Username, and Password).",
            )
            return

        try:
            if self.db_manager.add_new_login(url, username, password):
                QMessageBox.information(
                    self, "Success", "Password entry saved successfully."
                )
                self.update_table()
                self.clear_entry_fields()  # Clear the input fields after successful save
            else:
                QMessageBox.warning(
                    self,
                    "Database Error",
                    "Failed to save password entry. Please try again.",
                )
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"An unexpected error occurred: {str(e)}"
            )

    # Clear the input fields after successful save.
    def clear_entry_fields(self):
        self.entry_url.clear()
        self.entry_username.clear()
        self.entry_password.clear()

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

    """ Password Generation """

    # Generate a random password based on selected criteria.
    def generate_password(self):
        password_length = self.char_length.value()

        char_sets = [string.ascii_lowercase]
        required_chars = []

        if self.alpha_char.checkState() == Qt.CheckState.Checked:
            char_sets.append(string.ascii_uppercase)
            required_chars.append(random.choice(string.ascii_uppercase))

        if self.numerical_char.checkState() == Qt.CheckState.Checked:
            char_sets.append(string.digits)
            required_chars.append(random.choice(string.digits))

        if self.special_char.checkState() == Qt.CheckState.Checked:
            char_sets.append(string.punctuation)
            required_chars.append(random.choice(string.punctuation))

        # Combine all sets
        all_chars = "".join(char_sets)

        # Generate the main part of the password
        main_password = "".join(
            random.choice(all_chars)
            for _ in range(password_length - len(required_chars))
        )

        # Combine and shuffle password
        passw = "".join(required_chars + list(main_password))
        passw_list = list(passw)
        random.shuffle(passw_list)
        final_password = "".join(passw_list)

        self.password_field.setText(final_password)

        if self.integrate_password.checkState() == Qt.CheckState.Checked:
            self.entry_password.setText(final_password)

    # Update the label displaying current password length.
    def update_password_length(self, value):
        self.char_length_label.setText(f"Password Length: {str(value)}")
