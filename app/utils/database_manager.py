import csv

from PyQt6.QtCore import QSettings
from PyQt6.QtSql import QSqlDatabase, QSqlQuery
from PyQt6.QtWidgets import QMessageBox, QFileDialog
from cryptography.fernet import Fernet
import base64


class DatabaseManager:
    def __init__(self):
        self.db_name = "password.db"
        self.db = QSqlDatabase.addDatabase("QSQLITE")
        self.db.setDatabaseName(self.db_name)
        if not self.db.open():
            QMessageBox.critical(None, "Database Error", "Could not open database")
            return

        self.settings = QSettings("YourCompany", "YourApp")
        self.create_table()
        self.initialize_encryption()

    def create_table(self):
        query = QSqlQuery()
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
        return query.exec()

    def delete_login(self, row_id):
        query = QSqlQuery()
        query.prepare("DELETE FROM logins WHERE id = ?")
        query.addBindValue(row_id)
        return query.exec()

    def edit_login_password(self, row_id, password):
        encrypted_password = self.cipher.encrypt(password.encode()).decode()
        query = QSqlQuery()
        query.prepare("UPDATE logins SET encrypted_password = ? WHERE id = ?")
        query.addBindValue(encrypted_password)
        query.addBindValue(row_id)
        return query.exec()

    def load_table(self):
        query = QSqlQuery(
            "SELECT id, website, username, encrypted_password FROM logins ORDER BY id"
        )
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

    def export_to_csv(self):
        entries = self.load_table()

        file_path, _ = QFileDialog.getSaveFileName(
            None, "Save CSV File", "", "CSV Files (*.csv)"
        )

        if not file_path:
            QMessageBox.warning(
                None, "Export Cancelled", "Export was cancelled by the user."
            )
            return False

        if not file_path.endswith(".csv"):
            file_path += ".csv"

        try:
            with open(file_path, "w", newline="", encoding="utf-8") as csvfile:
                csv_writer = csv.writer(csvfile)
                csv_writer.writerow(["Website", "Username", "Password"])
                csv_writer.writerows(
                    [entry["website"], entry["username"], entry["password"]]
                    for entry in entries
                )

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

    def close(self):
        if self.db.isOpen():
            self.db.close()
