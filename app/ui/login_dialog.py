from PyQt6.QtWidgets import QDialog, QLineEdit, QLabel, QPushButton, QMessageBox, QGridLayout

class LoginDialog(QDialog):
    def __init__(self, password_manager, parent=None):
        super().__init__(parent)
        self.password_manager = password_manager
        self.setWindowTitle("Login")
        self.setFixedSize(450, 100)
        self.setup_ui()

    def setup_ui(self):
        layout = QGridLayout()
        self.password_label = QLabel("Enter Password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.try_login)

        layout.addWidget(self.password_label, 0, 0)
        layout.addWidget(self.password_input, 0, 1, 1, 2)
        layout.addWidget(self.login_button, 1, 1)
        self.setLayout(layout)

    def try_login(self):
        password = self.password_input.text()
        if self.password_manager.check_password(password):
            self.accept()
        else:
            QMessageBox.warning(self, "Login Failed", "Invalid password")