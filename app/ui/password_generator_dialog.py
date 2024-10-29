import string
import random
from PyQt6.QtWidgets import (QDialog, QGroupBox, QGridLayout, QLineEdit, QPushButton,
                             QCheckBox, QSlider, QLabel, QVBoxLayout, QMessageBox)
from PyQt6.QtCore import Qt

from app.utils.database_manager import DatabaseManager


class PasswordGenerationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Password Generation")
        self.setModal(True)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.create_password_generation_section())
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

    def generate_password(self, login_id=None):
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

        max_attempts = 100  # Prevent infinite loop
        for _ in range(max_attempts):
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

            # Check if the password has been used before
            if login_id is None or not DatabaseManager().is_password_previously_used(login_id, final_password):
                self.password_field.setText(final_password)
                return final_password

        # couldn't generate a unique password
        QMessageBox.warning(self, "Password Generation Failed",
                            "Unable to generate a unique password. Please try again or adjust the settings.")
        return None
    def update_password_length(self, value):
        self.char_length_label.setText(f"Password Length: {value}")

