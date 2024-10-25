from PyQt6.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initialize_UI()

    def initialize_UI(self):
        self.setWindowTitle("Demo Application")
        self.setFixedSize(300, 100)
        self.setup_ui()

    def setup_ui(self):
        central_widget = QWidget()
        layout = QVBoxLayout()
        welcome_label = QLabel("Welcome to the demo application!")
        layout.addWidget(welcome_label)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)