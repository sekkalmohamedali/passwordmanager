from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QGridLayout,
)
from PyQt6.QtCore import Qt
import re


class PasswordStrengthCheckerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.setFixedSize(400, 250)  # Increased height to accommodate feedback
        self.setWindowTitle("Password Strength Checker")
        self.setup_ui()

    def setup_ui(self):
        layout = QGridLayout(self)

        password_strength_label = QLabel("Password Strength:")

        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Enter password to check")

        self.check_button = QPushButton("Check Strength", self)
        self.check_button.clicked.connect(self.check_password_strength)

        self.result_label = QLabel(self)
        self.result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.feedback_label = QLabel(self)
        self.feedback_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.feedback_label.setWordWrap(True)

        layout.addWidget(password_strength_label, 0, 0, 1, 1)
        layout.addWidget(self.result_label, 0, 1, 1, 1)
        layout.addWidget(self.password_input, 1, 0, 1, 2)
        layout.addWidget(self.check_button, 2, 0, 1, 2, Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.feedback_label, 3, 0, 1, 2)  # Added feedback label

    def check_password_strength(self):
        password = self.password_input.text()

        # Initialize score
        score = 0
        feedback = []

        # Check length
        if len(password) < 8:
            feedback.append("Password is too short")
        elif len(password) >= 12:
            score += 2
            feedback.append("Good length")
        else:
            score += 1

        # Check for uppercase letters
        if re.search(r"[A-Z]", password):
            score += 1
        else:
            feedback.append("Add uppercase letters")

        # Check for lowercase letters
        if re.search(r"[a-z]", password):
            score += 1
        else:
            feedback.append("Add lowercase letters")

        # Check for numbers
        if re.search(r"\d", password):
            score += 1
        else:
            feedback.append("Add numbers")

        # Check for special characters
        if re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            score += 1
        else:
            feedback.append("Add special characters")

        # Check for repeating characters
        if re.search(r"(.)\1\1", password):
            score -= 1
            feedback.append("Avoid repeating characters")

        # Determine strength based on score
        if score < 2:
            strength = "Very Weak"
            color = "red"
        elif score < 4:
            strength = "Weak"
            color = "orange"
        elif score < 6:
            strength = "Medium"
            color = "yellow"
        elif score < 8:
            strength = "Strong"
            color = "lightgreen"
        else:
            strength = "Very Strong"
            color = "green"

        feedback_str = ", ".join(feedback) if feedback else "Excellent password!"

        self.result_label.setText(f"{strength}")
        self.result_label.setStyleSheet(f"color: {color}; font-weight: bold;")

        self.feedback_label.setText(f"Feedback: {feedback_str}")
