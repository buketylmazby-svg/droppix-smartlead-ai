import os
import sqlite3
from flask import Flask, jsonify, request
from flask_cors import CORS
from groq import Groq

app = Flask(__name__)
CORS(app)


def init_db():
  conn = sqlite3.connect('database.db')
  cursor = conn.cursor()
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            user_message TEXT,
            bot_response TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
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


init_db()


@app.route('/', methods=['GET'])
def home():
  return jsonify({'status': 'online', 'service': 'Droppix SmartLead AI Backend'})


@app.route('/api/chat', methods=['POST'])
def chat():
  try:
    data = request.get_json() or {}
    user_message = data.get('message', '')
    session_id = data.get('session_id', 'default_session')

    if not user_message:
      return jsonify({'error': 'Mesaj boş olamaz.'}), 400

    api_key = os.environ.get('GROQ_API_KEY')
    if not api_key:
      return (
          jsonify({
              'error': (
                  'GROQ_API_KEY Render Environment ortam değişkenlerinde'
                  ' bulunamadı.'
              )
          }),
          500,
      )

    client = Groq(api_key=api_key)

    # Groq üzerindeki güncel aktif modeller
    candidate_models = [
        'llama-3.3-70b-versatile',
        'llama-3.1-70b-versatile',
        'llama-3.2-3b-preview',
    ]

    bot_response = None
    errors = []

    for model_name in candidate_models:
      try:
        completion = client.chat.completions.create(
            model=model_name,
            messages=[
                {
                    'role': 'system',
                    'content': (
                        'Sen Droppix platformunun akıllı asistani Droppix'
                        " AI'sin."
                    ),
                },
                {'role': 'user', 'content': user_message},
            ],
        )
        bot_response = completion.choices[0].message.content
        if bot_response:
          break
      except Exception as err:
        errors.append(f'{model_name}: {str(err)}')

    if not bot_response:
      first_err = errors[0] if errors else 'Bilinmeyen hata'
      return (
          jsonify({'error': f'Groq bağlantı hatası. Detay: {first_err}'}),
          500,
      )

    # Veritabanı Kaydı
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
    return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
  app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
