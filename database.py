import sqlite3
from config import Config

def get_db_connection():
    """Veritabanı bağlantısı oluşturur ve satırları sözlük yapısında döndürür."""
    conn = sqlite3.connect(Config.DATABASE_URL)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Gerekli veritabanı tablolarını sıfırdan oluşturur."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Potansiyel Kullanıcı ve Partner Kayıtları (Leads)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            phone TEXT,
            user_type TEXT, -- 'b2c' (bireysel kullanıcı) veya 'b2b' (işletme/partner)
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 2. Sohbet Geçmişi (Chat History)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            sender TEXT, -- 'user' veya 'assistant'
            message TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()
    print("✅ Veritabanı tabloları (leads & chat_history) başarıyla oluşturuldu!")

if __name__ == '__main__':
    init_db()