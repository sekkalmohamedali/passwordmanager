from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QDialog,
    QLineEdit,
    QLabel,
    QPushButton,
    QMessageBox,
    QGridLayout,
)
from app.utils.database_manager import DatabaseManager
from app.utils.decorator_password_strength_checker import check_password_strength


class EditPassword(QDialog):
    def __init__(self, row, parent=None):
        super().__init__(parent)
        self.row = row
        self.parent = parent
        self.db_manager = parent.db_manager if parent else None
        self.setWindowTitle("Edit Password")
        self.setFixedSize(450, 200)
        self.setup_ui()

    def setup_ui(self):
        layout = QGridLayout()
        self.password_label = QLabel("New Password:")
        self.password_input = QLineEdit()
        self.password_confirm_label = QLabel("Confirm Password:")
        self.password_confirm_input = QLineEdit()

        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_confirm_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.password_input.textChanged.connect(self.check_password)
        self.password_strength_label = QLabel()

        self.confirm_button = QPushButton("Confirm")
        self.confirm_button.clicked.connect(self.change_password)

        layout.addWidget(self.password_label, 0, 0)
        layout.addWidget(self.password_input, 0, 1, 1, 2)
        layout.addWidget(self.password_confirm_label, 1, 0)
        layout.addWidget(self.password_confirm_input, 1, 1, 1, 2)
        layout.addWidget(QLabel("Password Strength:"), 2, 0)
        layout.addWidget(self.password_strength_label, 2, 1, 1, 2)
        layout.addWidget(self.confirm_button, 3, 1)

        self.setLayout(layout)

    def check_password(self):
        password = self.password_input.text()
        strength, color, _ = check_password_strength(password)
        self.password_strength_label.setText(strength)
        self.password_strength_label.setStyleSheet(
            f"color: {color}; font-weight: bold;"
        )

    def change_password(self):
        if self.pass_check():
            password = self.password_confirm_input.text()
            strength, _, feedback = check_password_strength(password)

            if strength in ["Very Weak", "Weak"]:
                reply = QMessageBox.question(
                    self,
                    "Weak Password",
                    f"Your password is {strength}. Do you want to continue?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                )
                if reply == QMessageBox.StandardButton.No:
                    return

            if self.db_manager and self.db_manager.edit_login_password(self.row, password):
                self.confirm_button.setText("Success")
                QTimer.singleShot(2000, self.close)
            else:
                QMessageBox.critical(
                    self,
                    "Error",
                    "Failed to update password. Please try again."
                )

    def pass_check(self):
        if self.password_input.text() == self.password_confirm_input.text():
            return True
        QMessageBox.critical(
            self,
            "Edit Password Error",
            "Passwords do not match",
            QMessageBox.StandardButton.Ok,
        )
        return False
