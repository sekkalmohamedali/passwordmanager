from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QScrollArea, QWidget

class DuplicatePasswordsDialog(QDialog):
    def __init__(self, duplicates):
        super().__init__()
        self.duplicates = duplicates
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Duplicate Passwords")
        self.setMinimumWidth(400)
        self.setMinimumHeight(300)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget(scroll)
        scroll_layout = QVBoxLayout(scroll_content)

        for dup in self.duplicates:
            password_label = QLabel(f"Password: {dup['password']}")
            count_label = QLabel(f"Used {dup['count']} times")
            websites_label = QLabel("Websites: " + ", ".join(dup['websites']))
            scroll_layout.addWidget(password_label)
            scroll_layout.addWidget(count_label)
            scroll_layout.addWidget(websites_label)
            scroll_layout.addWidget(QLabel(""))  # Spacer

        scroll_content.setLayout(scroll_layout)
        scroll.setWidget(scroll_content)

        layout.addWidget(scroll)

        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)

        self.setLayout(layout)
