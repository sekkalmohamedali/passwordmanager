from PyQt6.QtWidgets import (
    QDialog,
    QLineEdit,
    QLabel,
    QPushButton,
    QMessageBox,
    QGridLayout,
)


class ResetPasswordDialog(QDialog):
    def __init__(self, password_manager, parent=None):
        super().__init__(parent)
        self.password_manager = password_manager
        self.setWindowTitle("Reset Master Password")
        self.setFixedSize(450, 150)
        self.setup_ui()

    def setup_ui(self):
        layout = QGridLayout()
        self.old_password_label = QLabel("Enter Old Password:")
        self.old_password_input = QLineEdit()
        self.new_password_label = QLabel("Confirm Password:")
        self.new_password_input = QLineEdit()
        self.new_password_confirm_label = QLabel("Confirm Password:")
        self.new_password_confirm_input = QLineEdit()

        self.old_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.new_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.new_password_confirm_input.setEchoMode(QLineEdit.EchoMode.Password)


        self.create_button = QPushButton("Reset Password")
        self.create_button.clicked.connect(self.reset_password)

        layout.addWidget(self.old_password_label, 0, 0)
        layout.addWidget(self.old_password_input, 0, 1, 1, 2)
        layout.addWidget(self.new_password_label, 1, 0)
        layout.addWidget(self.new_password_input, 1, 1, 1, 2)
        layout.addWidget(self.new_password_confirm_label, 2,0)
        layout.addWidget(self.new_password_confirm_input, 2, 1, 1, 2)
        layout.addWidget(self.create_button,3,0,1,3)

        self.setLayout(layout)

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
            success = self.password_manager.password_reset(old_password, new_password)
            if success:
                QMessageBox.information(self, "Success", "Password reset successfully")
                self.accept()
            else:
                QMessageBox.warning(self, "Error", "Failed to reset password")

        # Clear input fields for security
        self.old_password_input.clear()
        self.new_password_input.clear()
        self.new_password_confirm_input.clear()