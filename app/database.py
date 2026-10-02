import sqlite3

class Database:
    def __init__(self, db_path="smartlead.db"):
        self.db_path = db_path
        self.init_db()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS leads (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    isim TEXT NOT NULL,
                    eposta TEXT NOT NULL,
                    notlar TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def lead_ekle(self, isim, eposta, notlar=""):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO leads (isim, eposta, notlar) VALUES (?, ?, ?)",
                (isim, eposta, notlar)
            )
            conn.commit()
            return cursor.lastrowid

db = Database()
