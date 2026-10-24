import sqlite3

class Database:
    # Yeni dosya adı: eski tablo yapısıyla çakışmasın diye
    def __init__(self, db_path="smartlead_v2.db"):
        self.db_path = db_path
        self.init_db()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # sütunlara isimle erişim
        return conn

    def init_db(self):
        with self.get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS leads (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    isim TEXT NOT NULL,
                    telefon TEXT NOT NULL,
                    mesaj TEXT,
                    tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def lead_ekle(self, isim, telefon, mesaj=""):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # ? işareti SQL Injection'a karşı korur
            cursor.execute(
                "INSERT INTO leads (isim, telefon, mesaj) VALUES (?, ?, ?)",
                (isim, telefon, mesaj)
            )
            conn.commit()
            return cursor.lastrowid

    def tum_leadler(self):
        with self.get_connection() as conn:
            satirlar = conn.execute(
                "SELECT id, isim, telefon, mesaj, tarih FROM leads ORDER BY id DESC"
            ).fetchall()
            # Satırları Wix'in okuyabileceği sözlüklere çevir
            return [dict(s) for s in satirlar]

db = Database()