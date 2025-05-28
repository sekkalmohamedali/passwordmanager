from PyQt6.QtWidgets import (
    QDialog,
    QLineEdit,
    QLabel,
    QPushButton,
    QMessageBox,
    QGridLayout,
)

from app.utils.password_strength_checker import check_password_strength


class ResetPasswordDialog(QDialog):
    def __init__(self, password_manager, parent=None):
        super().__init__(parent)
        self.password_manager = password_manager
        self.setWindowTitle("Reset Master Password")
        self.setFixedSize(450, 200)
        self.setup_ui()

    def setup_ui(self):
        layout = QGridLayout()
        self.old_password_label = QLabel("Enter Old Password:")
        self.old_password_input = QLineEdit()
        self.new_password_label = QLabel("New Password:")
        self.new_password_input = QLineEdit()
        self.new_password_confirm_label = QLabel("Confirm New Password:")
        self.new_password_confirm_input = QLineEdit()

        self.old_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.new_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.new_password_confirm_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.new_password_input.textChanged.connect(self.check_password)
        self.password_strength_label = QLabel()

        self.create_button = QPushButton("Reset Password")
        self.create_button.clicked.connect(self.reset_password)

        layout.addWidget(self.old_password_label, 0, 0)
        layout.addWidget(self.old_password_input, 0, 1, 1, 2)
        layout.addWidget(self.new_password_label, 1, 0)
        layout.addWidget(self.new_password_input, 1, 1, 1, 2)
        layout.addWidget(self.new_password_confirm_label, 2, 0)
        layout.addWidget(self.new_password_confirm_input, 2, 1, 1, 2)
        layout.addWidget(QLabel("Password Strength:"), 3, 0)
        layout.addWidget(self.password_strength_label, 3, 1, 1, 2)
        layout.addWidget(self.create_button, 4, 0, 1, 3)

        self.setLayout(layout)

    def check_password(self):
        password = self.new_password_input.text()
        strength, color, _ = check_password_strength(password)
        self.password_strength_label.setText(strength)
        self.password_strength_label.setStyleSheet(
            f"color: {color}; font-weight: bold;"
        )

    def reset_password(self):
        old_password = self.old_password_input.text()
        new_password = self.new_password_input.text()
        new_confirm = self.new_password_confirm_input.text()

        if not self.password_manager.check_password(old_password):
            QMessageBox.warning(self, "Error", "Original password is incorrect")
        elif new_password != new_confirm:
            QMessageBox.warning(self, "Error", "Passwords do not match")
        elif len(new_password) < 8:
            QMessageBox.warning(self, "Error", "Password must be at least 8 characters long")
        else:
            try:
                if self.password_manager.password_reset(old_password, new_password):
                    QMessageBox.information(self, "Success", 
                        "Password reset successfully. All stored passwords have been re-encrypted.")
                    self.accept()
                else:
                    QMessageBox.critical(self, "Error", 
                        "Failed to reset password. Your original password remains unchanged.")
            except Exception as e:
                QMessageBox.critical(self, "Error", 
                    f"An error occurred during password reset: {str(e)}\n"
                    "Your original password remains unchanged.")

        # Clear input fields for security
        self.old_password_input.clear()
        self.new_password_input.clear()
        self.new_password_confirm_input.clear()
