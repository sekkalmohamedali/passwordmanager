from PyQt6.QtWidgets import (
    QDialog,
    QLineEdit,
    QLabel,
    QPushButton,
    QMessageBox,
    QGridLayout,
)


class CreatePasswordDialog(QDialog):
    def __init__(self, password_manager, parent=None):
        super().__init__(parent)
        self.password_manager = password_manager
        self.setWindowTitle("Create Master Password")
        self.setFixedSize(450, 150)
        self.setup_ui()

    def setup_ui(self):
        layout = QGridLayout()
        self.password_label = QLabel("Enter New Password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_label = QLabel("Confirm Password:")
        self.confirm_input = QLineEdit()
        self.confirm_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.create_button = QPushButton("Create Password")
        self.create_button.clicked.connect(self.create_password)

        layout.addWidget(self.password_label, 0, 0)
        layout.addWidget(self.password_input, 0, 1, 1, 2)
        layout.addWidget(self.confirm_label, 1, 0)
        layout.addWidget(self.confirm_input, 1, 1, 1, 2)
        layout.addWidget(self.create_button, 2, 0, 1, 3)
        self.setLayout(layout)

    def create_password(self):
        password = self.password_input.text()
        confirm = self.confirm_input.text()
        if password != confirm:
            QMessageBox.warning(self, "Error", "Passwords do not match")
        elif len(password) < 8:
            QMessageBox.warning(
                self, "Error", "Password must be at least 8 characters long"
            )
        else:
            self.password_manager.create_password(password)
            self.accept()
