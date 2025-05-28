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


class DatabaseManager(DatabaseSubject):
    def __init__(self):
        super().__init__()  # Initialize the DatabaseSubject first
        self.db_name = "password.db"
        self.db = QSqlDatabase.addDatabase("QSQLITE")
        self.db.setDatabaseName(self.db_name)
        if not self.db.open():
            QMessageBox.critical(None, "Database Error", "Could not open database")
            return

        self.settings = QSettings("YourCompany", "YourApp")
        self.create_table()
        self.cipher = None

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
        """Initialize cipher with the master key"""
        key = base64.urlsafe_b64encode(key)
        self.cipher = Fernet(key)

    def initialize_encryption(self):
        master_key = self.settings.value("password_key")

        # Ensure key is properly formatted
        try:
            # Check if key is already in the correct format
            if len(master_key) == 32:
                master_key = base64.urlsafe_b64encode(master_key)
            elif len(master_key) != 44 or not isinstance(master_key, bytes):
                # If it's not 32 bytes (raw) or 44 bytes (base64 encoded), it's invalid
                raise ValueError("Invalid key length or type")

            self.cipher = Fernet(master_key)
        except Exception as e:
            raise ValueError(f"Invalid master key format: {e}")

    def add_new_login(self, website, username, password):
        encrypted_password = self.cipher.encrypt(password.encode()).decode()
        query = QSqlQuery()
        query.prepare(
            "INSERT INTO logins (website, username, encrypted_password) VALUES (?, ?, ?)"
        )
        query.addBindValue(website)
        query.addBindValue(username)
        query.addBindValue(encrypted_password)
        success = query.exec()
        if success:
            self.notify(DatabaseEvent.ENTRY_ADDED, {
                "website": website,
                "username": username
            })
        return success
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
            encrypted_password = self.cipher.encrypt(password.encode()).decode()
            query = QSqlQuery()
            query.prepare("UPDATE logins SET encrypted_password = ? WHERE id = ?")
            query.addBindValue(encrypted_password)
            query.addBindValue(row_id)
            return query.exec()
        except Exception as e:
            print(f"Error updating password: {str(e)}")
            return False

    def load_table(self):
        if not self.cipher:
            raise RuntimeError("Encryption key not set")
            
        entries = []
        query = QSqlQuery("SELECT id, website, username, encrypted_password FROM logins")
        
        while query.next():
            try:
                entries.append({
                    "id": query.value(0),
                    "website": query.value(1),
                    "username": query.value(2),
                    "password": self.cipher.decrypt(query.value(3).encode()).decode()
                })
            except Exception as e:
                print(f"Error decrypting entry {query.value(0)}: {str(e)}")
                continue
                
        return entries

    def get_password(self, row_id):
        query = QSqlQuery()
        query.prepare("SELECT encrypted_password FROM logins WHERE id = ?")
        query.addBindValue(row_id)
        if query.exec() and query.next():
            encrypted_password = query.value(0)
            decrypted_password = self.cipher.decrypt(
                encrypted_password.encode()
            ).decode()
            return decrypted_password
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
        entries = []
        while query.next():
            entries.append(
                {
                    "id": query.value(0),
                    "website": query.value(1),
                    "username": query.value(2),
                    "password": self.cipher.decrypt(query.value(3).encode()).decode(),
                }
            )
        return entries

    def is_password_previously_used(self, login_id, password):
        encrypted_password = self.cipher.encrypt(password.encode()).decode()
        query = QSqlQuery()
        query.prepare(
            "SELECT COUNT(*) FROM password_history WHERE login_id = ? AND encrypted_password = ?"
        )
        query.addBindValue(login_id)
        query.addBindValue(encrypted_password)

        if query.exec() and query.next():
            return query.value(0) > 0
        return False

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
                decrypted_pwd = self.cipher.decrypt(encrypted_pwd.encode()).decode()
                
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

    def reencrypt_database(self, old_key, new_key):
        """Re-encrypt all passwords with new key"""
        try:
            # Create ciphers for both keys
            old_cipher = Fernet(base64.urlsafe_b64encode(old_key))
            new_cipher = Fernet(base64.urlsafe_b64encode(new_key))
            
            # Get all passwords
            query = QSqlQuery("SELECT id, encrypted_password FROM logins")
            success = True
            
            while query.next():
                try:
                    login_id = query.value(0)
                    encrypted_pwd = query.value(1)
                    
                    # Decrypt with old key
                    decrypted = old_cipher.decrypt(encrypted_pwd.encode())
                    # Re-encrypt with new key
                    new_encrypted = new_cipher.encrypt(decrypted)
                    
                    # Update database
                    update = QSqlQuery()
                    update.prepare("UPDATE logins SET encrypted_password = ? WHERE id = ?")
                    update.addBindValue(new_encrypted.decode())
                    update.addBindValue(login_id)
                    
                    if not update.exec():
                        print(f"Failed to update password for ID {login_id}")
                        success = False
                        
                except Exception as e:
                    print(f"Error processing entry {login_id}: {str(e)}")
                    success = False
                    
            return success
            
        except Exception as e:
            print(f"Database re-encryption failed: {str(e)}")
            return False
