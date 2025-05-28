from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QListWidget, 
                            QPushButton, QMessageBox)

class RestoreBackupDialog(QDialog):
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.setWindowTitle("Restore from Backup")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        self.backup_list = QListWidget()
        for memento in self.db_manager.caretaker.get_all_mementos():
            self.backup_list.addItem(memento.description)
        
        restore_button = QPushButton("Restore Selected")
        restore_button.clicked.connect(self.restore_backup)
        
        layout.addWidget(self.backup_list)
        layout.addWidget(restore_button)

    def restore_backup(self):
        current_row = self.backup_list.currentRow()
        if current_row >= 0:
            memento = self.db_manager.caretaker.get_memento(current_row)
            if self.db_manager.restore_from_backup(memento):
                QMessageBox.information(self, "Success", "Backup restored successfully")
                self.accept()
            else:
                QMessageBox.warning(self, "Error", "Failed to restore backup")