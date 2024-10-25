import time

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


class EditPassword(QDialog):
    def __init__(self, row, parent=None):
        super().__init__(parent)
        self.row = row
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

        self.confirm_button = QPushButton("Confirm")
        self.confirm_button.clicked.connect(self.change_password)

        layout.addWidget(self.password_label, 0, 0)
        layout.addWidget(self.password_input, 0, 1, 1, 2)
        layout.addWidget(self.password_confirm_label, 1, 0)
        layout.addWidget(self.password_confirm_input, 1, 1, 1, 2)

        layout.addWidget(self.confirm_button, 2, 1)
        self.setLayout(layout)

    def change_password(self):
        if self.pass_check():
            DatabaseManager().edit_login_password(
                self.row, self.password_confirm_input.text()
            )
            self.confirm_button.setText("Success")
            QTimer.singleShot(2000, self.close)

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
