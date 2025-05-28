from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QComboBox, 
                            QPushButton, QLabel, QMessageBox)
from PyQt6.QtCore import QSettings
from app.utils.encryption_strategies import FernetEncryptionStrategy, AESEncryptionStrategy
import glob
import os
import shutil

class EncryptionSettingsDialog(QDialog):
    def __init__(self, parent=None, db_manager=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.setWindowTitle("Encryption Settings")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Encryption strategy selector
        self.strategy_label = QLabel("Select Encryption Algorithm:")
        self.strategy_combo = QComboBox()
        self.strategy_combo.addItems(["Fernet", "AES-256"])
        
        # Set current strategy
        current_strategy = type(self.db_manager.encryption_strategy).__name__
        current_index = 0 if "Fernet" in current_strategy else 1
        self.strategy_combo.setCurrentIndex(current_index)
        
        # Apply button
        self.apply_button = QPushButton("Apply Changes")
        self.apply_button.clicked.connect(self.apply_changes)
        
        layout.addWidget(self.strategy_label)
        layout.addWidget(self.strategy_combo)
        layout.addWidget(self.apply_button)
        self.setLayout(layout)

    def apply_changes(self):
        try:
            print("Starting encryption strategy change...")
            
            # 1. Store original strategy
            self._original_strategy = self.db_manager.encryption_strategy
            
            # 2. Create new strategy
            print("Creating new encryption strategy...")
            new_strategy = None
            if self.strategy_combo.currentText() == "Fernet":
                new_strategy = FernetEncryptionStrategy()
                print("Selected Fernet strategy")
            else:
                new_strategy = AESEncryptionStrategy()
                print("Selected AES strategy")
            
            # 3. Get current key from settings
            print("Getting current encryption key...")
            settings = QSettings("PyQtPasswordManager", "MasterPassword")
            current_key = settings.value("password_key")  # Changed from master_key
            
            if not current_key:
                raise ValueError("No encryption key found")
            
            print(f"Retrieved key of length: {len(current_key)} bytes")
            
            print("Initializing new strategy...")
            new_strategy.initialize_key(current_key)
            
            # 4. Start re-encryption process
            print("Starting database re-encryption...")
            success = self.db_manager.reencrypt_database(
                old_strategy=self.db_manager.encryption_strategy,
                new_strategy=new_strategy
            )
            
            if success:
                print("Re-encryption successful")
                self.db_manager.encryption_strategy = new_strategy
                QMessageBox.information(self, "Success", 
                    "Encryption strategy changed successfully.")
                self.accept()
            else:
                raise Exception("Database re-encryption failed")
                    
        except Exception as e:
            print(f"Error during encryption change: {str(e)}")
            QMessageBox.critical(self, "Error", 
                f"Failed to change encryption strategy: {str(e)}")
            self.handle_encryption_failure(e)

    def handle_encryption_failure(self, error: Exception):
        """Handle encryption change failures"""
        try:
            # Restore original strategy
            self.db_manager.encryption_strategy = self._original_strategy
            
            # Restore from backup if exists
            backup_files = glob.glob(f"{self.db_manager.db_name}.backup_*")
            if backup_files:
                latest_backup = max(backup_files, key=os.path.getctime)
                shutil.copy2(latest_backup, self.db_manager.db_name)
                
            QMessageBox.critical(self, "Error Recovery", 
                "Encryption change failed. Database restored to previous state.")
                
        except Exception as recovery_error:
            QMessageBox.critical(self, "Critical Error",
                f"Failed to recover from error: {str(recovery_error)}\n"
                "Please restore from your backup manually.")

    def validate_strategy_change(self) -> bool:
        """Validate before applying strategy change"""
        try:
            # Verify current encryption is working
            test_data = "test"
            encrypted = self.db_manager.encryption_strategy.encrypt(test_data)
            decrypted = self.db_manager.encryption_strategy.decrypt(encrypted)
            if test_data != decrypted:
                raise ValueError("Current encryption verification failed")
            return True
        except Exception as e:
            QMessageBox.critical(self, "Validation Error", 
                f"Cannot change encryption strategy: {str(e)}")
            return False