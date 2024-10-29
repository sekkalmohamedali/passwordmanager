from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QWidget,
)
from PyQt6.QtCore import Qt


class PasswordHistoryDialog(QDialog):
    def __init__(self, passwords, parent=None):
        super().__init__(parent)
        self.passwords = passwords

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Password History")
        self.setMinimumWidth(300)
        self.setMinimumHeight(200)
        self.setup_layout()

    def setup_layout(self):

        layout = QVBoxLayout()

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget(scroll)
        scroll_layout = QVBoxLayout(scroll_content)

        for passw, date in self.passwords:
            password_label = QLabel(f"Password: {passw}")
            date_label = QLabel(f"Used on: {date}")
            scroll_layout.addWidget(password_label)
            scroll_layout.addWidget(date_label)
            scroll_layout.addWidget(QLabel(""))  # Spacer

        scroll_content.setLayout(scroll_layout)
        scroll.setWidget(scroll_content)

        layout.addWidget(scroll)

        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)

        self.setLayout(layout)
