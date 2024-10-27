import string
import time
import random

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QDialog,
    QLineEdit,
    QLabel,
    QPushButton,
    QMessageBox,
    QGridLayout,
    QFormLayout,
    QHBoxLayout,
    QCheckBox,
    QGroupBox,
    QSlider,
    QVBoxLayout,
)

from app.utils.database_manager import DatabaseManager

class NewEntryDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.db_manager = parent.db_manager

        self.setWindowTitle("New Entry")
        self.setBaseSize(450, 400)
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout()
        form_layout = QFormLayout()

        self.entry_url = QLineEdit()
        self.entry_username = QLineEdit()
        self.entry_password = QLineEdit()

        form_layout.addRow("Website/URL:", self.entry_url)
        form_layout.addRow("Username/Email:", self.entry_username)
        form_layout.addRow("Password:", self.entry_password)

        # Create password generation section (initially hidden)
        self.password_generation_section = self.create_password_generation_section()

        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        entry_save_btn = QPushButton("Save")
        entry_save_btn.setFixedWidth(250)
        btn_layout.addWidget(entry_save_btn)

        main_layout.addLayout(form_layout)
        main_layout.addWidget(self.password_generation_section)
        main_layout.addLayout(btn_layout)

        entry_save_btn.clicked.connect(self.save_new_entry)

        self.setLayout(main_layout)

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

        # Layout
        layout.addWidget(self.password_field, 0, 0, 1, 2)
        layout.addWidget(self.generate_password_btn, 0, 2)

        layout.addWidget(self.alpha_char, 1, 0, 1, 1, Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.numerical_char, 2, 0, 1, 1, Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.special_char, 3, 0, 1, 1, Qt.AlignmentFlag.AlignLeft)

        layout.addWidget(self.char_length, 1, 1, 2, 2)
        layout.addWidget(self.char_length_label, 3, 1, 1, 2, Qt.AlignmentFlag.AlignCenter)

        group_box.setLayout(layout)
        return group_box

    def update_password_length(self, value):
        self.char_length_label.setText(f"Password Length: {value}")

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
            self.entry_password.setText(final_password)

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
                self.close()
                self.parent.update_table()
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