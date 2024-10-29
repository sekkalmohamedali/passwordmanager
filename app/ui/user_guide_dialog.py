from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QWidget,
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt


class UserGuideDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("User Guide - Password Manager")
        self.setFixedSize(600, 400)
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        # Title
        title = QLabel("Password Manager User Guide")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        scroll_layout.addWidget(title)

        # Add sections to the user guide
        self.add_section(
            scroll_layout,
            "Getting Started",
            [
                "1. Launch the Password Manager application.",
                "2. Create a master password to secure your vault.",
                "3. Use this master password to log in each time you open the app.",
            ],
        )

        self.add_section(
            scroll_layout,
            "Adding a New Password",
            [
                "1. Click the 'Add New' button.",
                "2. Enter the website URL, username, and password.",
                "3. Click 'Save' to store the new entry.",
            ],
        )

        self.add_section(
            scroll_layout,
            "Viewing and Editing Passwords",
            [
                "1. Select an entry from the main list.",
                "2. Click 'View' to see the full details.",
                "3. To edit, click 'Edit', make your changes, and click 'Save'.",
            ],
        )

        self.add_section(
            scroll_layout,
            "Generating Secure Passwords",
            [
                "1. When adding or editing an entry, click 'Generate Password'.",
                "2. Adjust the settings for length and character types.",
                "3. Click 'Generate' to create a new secure password.",
            ],
        )

        self.add_section(
            scroll_layout,
            "Searching for Entries",
            [
                "1. Use the search bar at the top of the main window.",
                "2. Type in keywords related to the website or username.",
                "3. Results will filter as you type.",
            ],
        )

        self.add_section(
            scroll_layout,
            "Backing Up Your Data",
            [
                "1. Go to File > Backup Database.",
                "2. Choose a secure location to save your backup file.",
                "3. Regularly backup to prevent data loss.",
            ],
        )

        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)

        # Close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        main_layout.addWidget(close_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(main_layout)

    def add_section(self, layout, title, content):
        section_title = QLabel(title)
        section_title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(section_title)

        for item in content:
            item_label = QLabel(item)
            item_label.setWordWrap(True)
            layout.addWidget(item_label)

        layout.addWidget(QLabel(""))  # Add some space between sections
