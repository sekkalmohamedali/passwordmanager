import csv
import datetime
import json
import os
import shutil
import xml.etree.ElementTree as ET
from PyQt6.QtCore import QSettings
from PyQt6.QtWidgets import QMessageBox, QFileDialog
import base64
from cryptography.fernet import Fernet
from PyQt6.QtSql import QSqlQuery, QSqlDatabase
from app.utils.observer import DatabaseSubject, DatabaseEvent
from app.utils.encryption_strategies import EncryptionStrategy, FernetEncryptionStrategy
from app.utils.decorator_password_strength_checker import check_password_strength


class DatabaseManager(DatabaseSubject):
    def __init__(self, encryption_strategy: EncryptionStrategy = None):
        super().__init__()  # Initialize the DatabaseSubject first
        self.db_name = "password.db"
        self.db = QSqlDatabase.addDatabase("QSQLITE")
        self.db.setDatabaseName(self.db_name)
        if not self.db.open():
            QMessageBox.critical(None, "Database Error", "Could not open database")
            return

        # Use the same settings as MasterLogin
        self.settings = QSettings("PyQtPasswordManager", "MasterPassword")
        self.create_table()
        self.encryption_strategy = encryption_strategy or FernetEncryptionStrategy()
        
        # Try to initialize with existing key
        key = self.settings.value("password_key")
        if key:
            try:
                self.encryption_strategy.initialize_key(key)
            except Exception as e:
                print(f"Error initializing encryption key: {str(e)}")
                raise

    def create_table(self):
        query = QSqlQuery()
        # Create logins table only
        query.exec(
            """
            CREATE TABLE IF NOT EXISTS logins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                website TEXT NOT NULL,
                username TEXT NOT NULL,
                encrypted_password TEXT NOT NULL
            )
            """
        )
        # Remove password history table creation
    
    def set_encryption_key(self, key):
        """Initialize encryption strategy with the master key"""
        try:
            print(f"Setting encryption key, length: {len(key)} bytes")
            self.settings.setValue("password_key", key)  # Store the key
            self.encryption_strategy.initialize_key(key)
            print("Encryption key initialized successfully")
        except Exception as e:
            print(f"Error initializing encryption key: {str(e)}")
            raise

    def check_password_strength(self, password: str) -> tuple[str, str, list]:
        """Check password strength and return results"""
        strength, color, feedback = check_password_strength(password)
        self.notify(DatabaseEvent.PASSWORD_STRENGTH_CHANGED, {
            "strength": strength,
            "color": color,
            "feedback": feedback
        })
        return strength, color, feedback

    def add_new_login(self, website, username, password):
        try:
            # Check password strength before adding
            strength, _, _ = self.check_password_strength(password)
            
            encrypted_password = self.encryption_strategy.encrypt(password)
            query = QSqlQuery()
            query.prepare(
                "INSERT INTO logins (website, username, encrypted_password) VALUES (?, ?, ?)"
            )
            query.addBindValue(website)
            query.addBindValue(username)
            query.addBindValue(encrypted_password)
            
            if query.exec():
                # Notify observers about the new entry
                self.notify(DatabaseEvent.ENTRY_ADDED, {
                    "website": website,
                    "username": username,
                    "strength": strength
                })
                return True
            return False
        except Exception as e:
            print(f"Error adding login: {str(e)}")
            return False
        # Remove add_password_to_history call

    def delete_login(self, row_id):
        query = QSqlQuery()
        query.prepare("DELETE FROM logins WHERE id = ?")
        query.addBindValue(row_id)
        success = query.exec()
        if success:
            self.notify(DatabaseEvent.ENTRY_DELETED, {"id": row_id})
        return success

    def edit_login_password(self, row_id, password):
        """Update password for an existing entry"""
        try:
            encrypted_password = self.encryption_strategy.encrypt(password)
            query = QSqlQuery()
            query.prepare("UPDATE logins SET encrypted_password = ? WHERE id = ?")
            query.addBindValue(encrypted_password)
            query.addBindValue(row_id)
            return query.exec()
        except Exception as e:
            print(f"Error updating password: {str(e)}")
            return False

    def load_table(self):
        """Load all entries from database"""
        if not self.encryption_strategy:
            raise RuntimeError("Encryption strategy not initialized")
            
        entries = []
        query = QSqlQuery("SELECT id, website, username, encrypted_password FROM logins")
        
        while query.next():
            try:
                encrypted_password = query.value(3)
                decrypted_password = self.encryption_strategy.decrypt(encrypted_password)
                
                entries.append({
                    "id": query.value(0),
                    "website": query.value(1),
                    "username": query.value(2),
                    "password": decrypted_password
                })
            except Exception as e:
                print(f"Error decrypting entry {query.value(0)}: {str(e)}")
                continue
                
        return entries

    def get_password(self, row_id):
        """Get decrypted password for a given row ID"""
        try:
            query = QSqlQuery()
            query.prepare("SELECT encrypted_password FROM logins WHERE id = ?")
            query.addBindValue(row_id)
            if query.exec() and query.next():
                encrypted_password = query.value(0)
                # Handle the case where encrypted_password might be bytes or string
                return self.encryption_strategy.decrypt(encrypted_password)
            return None
        except Exception as e:
            print(f"Error retrieving password: {str(e)}")
            return None

    def export_data(self):
        entries = self.load_table()

        file_path, file_type = QFileDialog.getSaveFileName(
            None,
            "Export File",
            "",
            "CSV Files (*.csv);;JSON Files (*.json);;XML Files (*.xml)",
        )

        if not file_path:
            QMessageBox.warning(
                None, "Export Cancelled", "Export was cancelled by the user."
            )
            return False

        try:
            if file_path.endswith(".csv"):
                self.export_to_csv(file_path, entries)
            elif file_path.endswith(".json"):
                self.export_to_json(file_path, entries)
            elif file_path.endswith(".xml"):
                self.export_to_xml(file_path, entries)
            else:
                raise ValueError("Unsupported file format")

            QMessageBox.information(
                None, "Export Success", f"Data exported successfully to {file_path}"
            )
            return True

        except PermissionError:
            QMessageBox.critical(
                None,
                "Export Failed",
                "Permission denied. The file may be open in another program.",
            )
            return False
        except Exception as e:
            QMessageBox.critical(
                None,
                "Export Failed",
                f"An error occurred while saving the file: {str(e)}",
            )
            return False

    def export_to_csv(self, file_path, entries):
        with open(file_path, "w", newline="", encoding="utf-8") as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(["Website", "Username", "Password"])
            csv_writer.writerows(
                [entry["website"], entry["username"], entry["password"]]
                for entry in entries
            )

    def export_to_json(self, file_path, entries):
        data = [
            {
                "Website": entry["website"],
                "Username": entry["username"],
                "Password": entry["password"],
            }
            for entry in entries
        ]
        with open(file_path, "w", encoding="utf-8") as jsonfile:
            json.dump(data, jsonfile, indent=2)

    def export_to_xml(self, file_path, entries):
        root = ET.Element("passwords")
        for entry in entries:
            entry_elem = ET.SubElement(root, "entry")
            ET.SubElement(entry_elem, "Website").text = entry["website"]
            ET.SubElement(entry_elem, "Username").text = entry["username"]
            ET.SubElement(entry_elem, "Password").text = entry["password"]

        tree = ET.ElementTree(root)
        tree.write(file_path, encoding="utf-8", xml_declaration=True)

    def import_data(self):
        file_path, file_type = QFileDialog.getOpenFileName(
            None,
            "Import File",
            "",
            "CSV Files (*.csv);;JSON Files (*.json);;XML Files (*.xml)",
        )

        if not file_path:
            return False

        try:
            if file_path.endswith(".csv"):
                self.import_from_csv(file_path)
            elif file_path.endswith(".json"):
                self.import_from_json(file_path)
            elif file_path.endswith(".xml"):
                self.import_from_xml(file_path)
            else:
                raise ValueError("Unsupported file format")

            QMessageBox.information(
                None, "Import Success", "Data imported successfully"
            )
            return True

        except Exception as e:
            QMessageBox.critical(None, "Import Failed", f"An error occurred: {str(e)}")
            return False

    def import_from_csv(self, file_path):
        with open(file_path, "r", newline="", encoding="utf-8") as csvfile:
            csv_reader = csv.DictReader(csvfile)
            for row in csv_reader:
                self.add_new_login(row["Website"], row["Username"], row["Password"])

    def import_from_json(self, file_path):
        with open(file_path, "r", encoding="utf-8") as jsonfile:
            data = json.load(jsonfile)
            for entry in data:
                self.add_new_login(
                    entry["Website"], entry["Username"], entry["Password"]
                )

    def import_from_xml(self, file_path):
        tree = ET.parse(file_path)
        root = tree.getroot()
        for entry in root.findall("entry"):
            website = entry.find("Website").text
            username = entry.find("Username").text
            password = entry.find("Password").text
            self.add_new_login(website, username, password)

    def backup_database(self):
        if not self.db.isOpen():
            QMessageBox.critical(None, "Backup Error", "Database is not open")
            return False

        backup_dir = QFileDialog.getExistingDirectory(None, "Select Backup Directory")
        if not backup_dir:
            return False

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"password_backup_{timestamp}.db"
        backup_path = os.path.join(backup_dir, backup_filename)

        try:
            self.db.close()
            shutil.copy2(self.db_name, backup_path)
            self.db.open()
            QMessageBox.information(
                None, "Backup Success", f"Database backed up to {backup_path}"
            )
            return True
        except Exception as e:
            QMessageBox.critical(None, "Backup Error", f"An error occurred: {str(e)}")
            self.db.open()
            return False

    def restore_database(self):
        if self.db.isOpen():
            self.db.close()

        backup_file, _ = QFileDialog.getOpenFileName(
            None, "Select Backup File", "", "Database Files (*.db)"
        )
        if not backup_file:
            self.db.open()
            return False

        try:
            shutil.copy2(backup_file, self.db_name)
            self.db.open()
            QMessageBox.information(
                None, "Restore Success", "Database restored successfully"
            )
            return True
        except Exception as e:
            QMessageBox.critical(None, "Restore Error", f"An error occurred: {str(e)}")
            self.db.open()
            return False

    def sort_by_website(self):
        query = QSqlQuery(
            """
            SELECT id, website, username, encrypted_password 
            FROM logins 
            ORDER BY website
            """
        )
        return self._process_query_results(query)

    def sort_by_username(self):
        query = QSqlQuery(
            """
            SELECT id, website, username, encrypted_password 
            FROM logins 
            ORDER BY username
            """
        )
        return self._process_query_results(query)

    def _process_query_results(self, query):
        """Process query results and handle encryption/decryption"""
        print("\n=== Processing Query Results ===")
        entries = []
        while query.next():
            try:
                encrypted_password = query.value(3)
                print(f"Processing entry ID: {query.value(0)}")
                
                # Handle string/bytes conversion for decryption
                try:
                    if isinstance(encrypted_password, str):
                        decrypted = self.encryption_strategy.decrypt(encrypted_password)
                    else:
                        decrypted = self.encryption_strategy.decrypt(encrypted_password.decode())
                
                    # Ensure final result is string
                    if isinstance(decrypted, bytes):
                        decrypted = decrypted.decode()
                    
                    entries.append({
                        "id": query.value(0),
                        "website": query.value(1),
                        "username": query.value(2),
                        "password": decrypted
                    })
                    print(f"Successfully processed entry {query.value(0)}")
                    
                except Exception as e:
                    print(f"Error decrypting entry {query.value(0)}: {str(e)}")
                    continue
                
            except Exception as e:
                print(f"Error processing entry: {str(e)}")
                continue
            
        print(f"Successfully processed {len(entries)} entries")
        return entries

    def is_password_previously_used(self, login_id, password):
        # Change from self.cipher to self.encryption_strategy
        encrypted_password = self.encryption_strategy.encrypt(password)
        query = QSqlQuery()
        query.prepare(
            "SELECT COUNT(*) FROM password_history WHERE login_id = ? AND encrypted_password = ?"
        )
        query.addBindValue(login_id)
        query.addBindValue(encrypted_password)
        return query.exec() and query.next() and query.value(0) > 0

    def get_password_history(self, login_id):
        query = QSqlQuery()
        query.prepare("""
            SELECT encrypted_password, date_used 
            FROM password_history 
            WHERE login_id = ? 
            ORDER BY date_used DESC
        """)
        query.addBindValue(login_id)
        
        history = []
        if query.exec():
            while query.next():
                encrypted_password = query.value(0)
                date = query.value(1)
                password = self.cipher.decrypt(encrypted_password.encode()).decode()
                history.append({"password": password, "date": date})
        return history

    def find_duplicate_passwords(self):
        """Find passwords that are used multiple times"""
        # First get all entries
        query = QSqlQuery("SELECT id, website, encrypted_password FROM logins")
        
        # Dictionary to store decrypted passwords and their occurrences
        password_map = {}
        
        while query.next():
            try:
                entry_id = query.value(0)
                website = query.value(1)
                encrypted_pwd = query.value(2)
                
                # Decrypt the password
                decrypted_pwd = self.encryption_strategy.decrypt(encrypted_pwd)
                
                # Add to password map
                if decrypted_pwd in password_map:
                    password_map[decrypted_pwd]["count"] += 1
                    password_map[decrypted_pwd]["websites"].append(website)
                else:
                    password_map[decrypted_pwd] = {
                        "count": 1,
                        "websites": [website]
                    }
            
            except Exception as e:
                print(f"Error processing entry {entry_id}: {str(e)}")
                continue
        
        # Filter only passwords used multiple times
        duplicates = [
            {
                "password": pwd,
                "count": data["count"],
                "websites": data["websites"]
            }
            for pwd, data in password_map.items()
            if data["count"] > 1
        ]
        
        return duplicates

    def close(self):
        if self.db.isOpen():
            self.db.close()

    def reencrypt_database(self, old_strategy, new_strategy):
        """Re-encrypt entire database with new strategy"""
        print("\n=== Starting Database Re-encryption Process ===")
        
        # Store original strategy before validation
        original_strategy = self.encryption_strategy
        
        if not self.validate_encryption_change():
            print("Validation failed, aborting re-encryption")
            return False

        self.db.transaction()
        
        try:
            # 1. Create backup
            if not self._create_backup():
                raise ValueError("Failed to create backup")
            
            # 2. Get all passwords
            print("Retrieving all passwords...")
            query = QSqlQuery("SELECT id, encrypted_password FROM logins")
            updates = []
            
            # 3. Process each password
            while query.next():
                try:
                    login_id = query.value(0)
                    encrypted_pwd = query.value(1)
                    print(f"Processing entry ID: {login_id}")
                    
                    # Decrypt with old strategy
                    decrypted = old_strategy.decrypt(encrypted_pwd)
                    print(f"Successfully decrypted entry {login_id}")
                    
                    # Encrypt with new strategy
                    new_encrypted = new_strategy.encrypt(decrypted)
                    print(f"Successfully re-encrypted entry {login_id}")
                    
                    updates.append((login_id, new_encrypted))
                    
                except Exception as e:
                    raise Exception(f"Failed processing entry {login_id}: {str(e)}")
        
            # 4. Apply updates
            print("Applying updates to database...")
            for login_id, new_encrypted in updates:
                update_query = QSqlQuery()
                update_query.prepare(
                    "UPDATE logins SET encrypted_password = ? WHERE id = ?"
                )
                update_query.addBindValue(new_encrypted)
                update_query.addBindValue(login_id)
                if not update_query.exec():
                    raise Exception(f"Failed to update entry {login_id}")
        
            self.db.commit()
            self.encryption_strategy = new_strategy  # Update to new strategy
            print("Re-encryption process completed successfully")
            return True
        
        except Exception as e:
            error_msg = f"Re-encryption failed: {str(e)}"
            print(error_msg)
            print("Rolling back changes...")
            self.db.rollback()
            self.encryption_strategy = original_strategy  # Now original_strategy is in scope
            self.handle_encryption_error("re-encryption", e)
            return False

    def validate_encryption_change(self) -> bool:
        """Validate database state before encryption change"""
        try:
            print("Starting encryption change validation...")
            
            # 1. Check database state
            if not self.db.isOpen():
                raise ValueError("Database is not accessible")
            print("Database accessibility check: PASSED")
            
            # 2. Check if there's enough disk space
            db_path = os.path.abspath(self.db_name)  # Get full path
            print(f"Database path: {db_path}")
            
            db_size = os.path.getsize(db_path)
            free_space = shutil.disk_usage("E:\\").free  # Use your drive letter
            if free_space < (db_size * 3):
                raise ValueError(f"Insufficient disk space. Need: {db_size * 3}, Available: {free_space}")
            print("Disk space check: PASSED")
            
            # 3. Verify backup directory exists
            backup_dir = os.path.join("E:", "s8", "design_patterns", "passwordmanager", "backups")
            print(f"Attempting to create/verify backup directory: {backup_dir}")
            
            if not os.path.exists(backup_dir):
                try:
                    os.makedirs(backup_dir, exist_ok=True)
                    print(f"Created backup directory: {backup_dir}")
                except Exception as e:
                    raise ValueError(f"Failed to create backup directory: {str(e)}")
            print("Backup directory check: PASSED")
            
            # 4. Test current encryption
            try:
                test_data = "test_encryption"
                encrypted = self.encryption_strategy.encrypt(test_data)
                decrypted = self.encryption_strategy.decrypt(encrypted)
                if decrypted != test_data:
                    raise ValueError("Current encryption verification failed")
                print("Encryption verification: PASSED")
            except Exception as e:
                raise ValueError(f"Encryption test failed: {str(e)}")
            
            print("All validation checks passed successfully")
            return True
            
        except Exception as e:
            error_msg = f"Validation failed: {str(e)}"
            print(error_msg)
            return False

    def handle_encryption_error(self, operation: str, error: Exception) -> None:
        """Handle encryption/decryption errors"""
        error_msg = f"Encryption error during {operation}: {str(error)}"
        print(error_msg)
        QMessageBox.critical(None, "Encryption Error", error_msg)
        self.notify(DatabaseEvent.DATABASE_ENCRYPTED, {"success": False, "error": error_msg})

    def _create_backup(self) -> bool:
        """Create backup before re-encryption"""
        try:
            print("Creating database backup...")
            backup_dir = os.path.join("E:", "s8", "design_patterns", "passwordmanager", "backups")
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = os.path.join(backup_dir, f"pre_encryption_change_{timestamp}.db")
            
            print(f"Attempting to create backup at: {backup_path}")
            
            # Close connection temporarily
            self.db.close()
            shutil.copy2(self.db_name, backup_path)
            self.db.open()
            
            print(f"Backup created successfully at: {backup_path}")
            return True
        except Exception as e:
            error_msg = f"Backup creation failed: {str(e)}"
            print(error_msg)
            self.db.open()  # Ensure database is reopened
            return False

