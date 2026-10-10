
import mysql.connector
from mysql.connector import Error


class DatabaseConnection:
    def __init__(
        self,
        host="127.0.0.1",
        user="root",
        password="",
        database="news",
        port=3306
    ):
        self.config = {
            "host": host,
            "user": user,
            "password": password,
            "database": database,
            "port": port,
            "use_pure": True
        }

    def get_connection(self):
        try:
            return mysql.connector.connect(**self.config)
        except Error as e:
            print(f"Loi ket noi database: {e}")
            return None
