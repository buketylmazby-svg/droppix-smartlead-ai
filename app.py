import os
import sqlite3
from flask import Flask, jsonify, request
from flask_cors import CORS
from groq import Groq

app = Flask(__name__)
CORS(app)  # Tarayıcı erişim izinleri (CORS)


# Veritabanı ve Tabloları Otomatik Oluşturma
def init_db():
  conn = sqlite3.connect('database.db')
  cursor = conn.cursor()

  # Chat geçmişi tablosu
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            user_message TEXT,
            bot_response TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

  # Lead (Müşteri Adayı) tablosu
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            contact TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

  conn.commit()
  conn.close()


# Sunucu her başladığında tabloları kontrol et/oluştur
init_db()

# Groq API istemcisi
groq_client = Groq(api_key=os.environ.get('GROQ_API_KEY'))


@app.route('/', methods=['GET'])
def home():
  return jsonify({"status": "online", "service": "Droppix SmartLead AI Backend"})


@app.route('/api/chat', methods=['POST'])
def chat():
  try:
    data = request.get_json() or {}
    user_message = data.get('message', '')
    session_id = data.get('session_id', 'default_session')

    if not user_message:
      return jsonify({'error': 'Mesaj boş olamaz.'}), 400

    # Groq AI Model Çağrısı
    completion = groq_client.chat.completions.create(
        model='llama-3.3-70b-versatile',
        messages=[
            {
                'role': 'system',
                'content': (
                    'Sen Droppix platformunun akıllı asistani Droppix AI\'sin.'
                    ' Kullanıcılara nazik, yardımsever ve özgün yanıtlar ver.'
                ),
            },
            {'role': 'user', 'content': user_message},
        ],
    )

    bot_response = completion.choices[0].message.content

    # Veritabanına Kaydetme
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO chat_history (session_id, user_message, bot_response)'
        ' VALUES (?, ?, ?)',
        (session_id, user_message, bot_response),
    )
    conn.commit()
    conn.close()

    return jsonify({'response': bot_response})

  except Exception as e:
    print(f'Chat Hata: {e}')
    return jsonify({'error': str(e)}), 500


@app.route('/api/lead', methods=['POST'])
def lead():
  try:
    data = request.get_json() or {}
    name = data.get('name', '')
    contact = data.get('contact', '')
    notes = data.get('notes', '')

    if not name or not contact:
      return jsonify({'error': 'İsim ve iletişim bilgisi zorunludur.'}), 400

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO leads (name, contact, notes) VALUES (?, ?, ?)',
        (name, contact, notes),
    )
    conn.commit()
    conn.close()

    return jsonify({'status': 'success', 'message': 'Lead kaydedildi.'})

  except Exception as e:
    print(f'Lead Hata: {e}')
    return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
  app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
