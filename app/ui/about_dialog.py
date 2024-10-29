from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("About Password Manager")
        self.setFixedSize(400, 300)
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(10)

        # App name
        app_name = QLabel("Password Manager")
        app_name.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        main_layout.addWidget(app_name, alignment=Qt.AlignmentFlag.AlignCenter)

        # Version
        version = QLabel("Version 1.0.0")
        version.setFont(QFont("Arial", 10))
        main_layout.addWidget(version, alignment=Qt.AlignmentFlag.AlignCenter)

        # Description
        description = QLabel("A secure and user-friendly password management solution.")
        description.setWordWrap(True)
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(description)

        # License Information
        license_info = QLabel("Licensed under the terms of the GNU General Public License v3.0.")
        license_info.setWordWrap(True)
        license_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(license_info)

        # Author Information
        author_info = QLabel("© 2024 Mckenzie Turner - Open Source")
        author_info.setWordWrap(True)
        author_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(author_info)

        # Close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        button_layout.addStretch()

        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)