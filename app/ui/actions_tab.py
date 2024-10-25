from PyQt6.QtCore import QFile, pyqtSignal, QDir, QSize
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton


class ActionsTab(QWidget):
    view_clicked = pyqtSignal(int)
    edit_clicked = pyqtSignal(int)
    delete_clicked = pyqtSignal(int)

    def __init__(self, row, parent=None):
        super().__init__(parent)
        self.row = row
        self.setup()

    def setup(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        button_data = [
            ("View", self.on_view_clicked),
            ("Edit", self.on_edit_clicked),
            ("Delete", self.on_delete_clicked),
        ]

        for button_name, click_handler in button_data:
            btn = QPushButton()
            icon_path = QDir.current().filePath(
                f"images/{button_name.lower()}_icon.png"
            )
            if QFile.exists(icon_path):
                pixmap = QPixmap(icon_path)
                btn.setIcon(QIcon(pixmap))
            else:
                print(f"Warning: Icon file not found: {icon_path}")

            btn.setIconSize(QSize(18, 18))
            btn.setFixedSize(25, 25)
            btn.setToolTip(button_name)
            btn.clicked.connect(click_handler)
            layout.addWidget(btn)

        self.setLayout(layout)

    def on_view_clicked(self):
        self.view_clicked.emit(self.row)

    def on_edit_clicked(self):
        self.edit_clicked.emit(self.row)

    def on_delete_clicked(self):
        self.delete_clicked.emit(self.row)
