from PyQt6.QtSql import QSqlDatabase, QSqlQuery
from PyQt6.QtWidgets import QMessageBox

class DatabaseManager:
    def __init__(self):
        self.db_name = "password.db"
        self.db = QSqlDatabase.addDatabase("QSQLITE")
        self.db.setDatabaseName(self.db_name)
        if not self.db.open():
            QMessageBox.critical(None, "Database Error", "Could not open database")
            return

        self.create_table()

    def create_table(self):
        query = QSqlQuery()
        query.exec("""
            CREATE TABLE IF NOT EXISTS logins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                website TEXT NOT NULL,
                username TEXT NOT NULL,
                password TEXT NOT NULL
            )
        """)

    def add_new_login(self, website, username, password):
        query = QSqlQuery()
        query.prepare("INSERT INTO logins (website, username, password) VALUES (?, ?, ?)")
        query.addBindValue(website)
        query.addBindValue(username)
        query.addBindValue(password)
        return query.exec()

    def delete_login(self, row_id):
        query = QSqlQuery()
        query.prepare("DELETE FROM logins WHERE id = ?")
        query.addBindValue(row_id)
        success = query.exec()
        if success:
            self.update_ids()
        return success

    def edit_login_password(self, row_id, password):
        query = QSqlQuery()
        query.prepare("UPDATE logins SET password = ? WHERE id = ?")
        query.addBindValue(password)
        query.addBindValue(row_id)
        return query.exec()

    def load_table(self):
        query = QSqlQuery("SELECT id, website, username, password FROM logins ORDER BY id")
        return query

    def update_ids(self):
        query = QSqlQuery()
        query.exec("BEGIN TRANSACTION")
        query.exec("CREATE TEMPORARY TABLE temp_logins AS SELECT * FROM logins ORDER BY id")
        query.exec("DELETE FROM logins")
        query.exec("INSERT INTO logins SELECT NULL, website, username, password FROM temp_logins")
        query.exec("DROP TABLE temp_logins")
        query.exec("COMMIT")

    def close(self):
        if self.db.isOpen():
            self.db.close()
