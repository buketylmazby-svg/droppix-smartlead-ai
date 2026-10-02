import sqlite3

def get_db():
    """Veritabanı bağlantısı oluşturur ve sütun isimleriyle erişim sağlar."""
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db(app=None):
    """'leads' tablosunu veritabanında oluşturur (yoksa)."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            isim TEXT NOT NULL,
            telefon TEXT NOT NULL,
            mesaj TEXT,
            tarih DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def lead_ekle(isim, telefon, mesaj=""):
    """Yeni kayıt ekler (SQL Injection'a karşı ? parametresi kullanılır)."""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO leads (isim, telefon, mesaj) VALUES (?, ?, ?)",
            (isim, telefon, mesaj)
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Veritabanı ekleme hatası: {e}")
        return False

def tum_leadler():
    """Tüm kayıtları en yeniden eskiye sıralı olarak liste halinde getirir."""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, isim, telefon, mesaj, tarih FROM leads ORDER BY id DESC")
        rows = cursor.fetchall()
        
        # JSON dönüştürmeye uygun sözlük (dict) listesi oluştur
        leadler = [dict(row) for row in rows]
        conn.close()
        return leadler
    except Exception as e:
        print(f"Veritabanı listeleme hatası: {e}")
        return []
