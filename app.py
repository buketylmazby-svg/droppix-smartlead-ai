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

    # 1. Groq hesabında aktif olan modelleri doğrudan sorgula
    try:
      models_page = client.models.list()
      available_models = [m.id for m in models_page.data]
    except Exception as api_err:
      return (
          jsonify({
              'error': (
                  'Groq API Key doğrulaması başarısız. Lütfen Render'
                  f' Environment ayarlarınızı kontrol edin. Detay: {str(api_err)}'
              )
          }),
          500,
      )

    if not available_models:
      return (
          jsonify({'error': 'Groq hesabınızda aktif kullanımda model bulunamadı.'}),
          500,
      )

    # 2. Aktif modeller arasından uygun olanı seç
    chosen_model = available_models[0]
    preferred_keywords = [
        'llama-3.3',
        'llama-3.1',
        'llama-3.2',
        'mixtral',
        'gemma',
    ]

    for kw in preferred_keywords:
      matched = [m for m in available_models if kw in m]
      if matched:
        chosen_model = matched[0]
        break

    # 3. Yanıtı üret
    completion = client.chat.completions.create(
        model=chosen_model,
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

    # 4. Veritabanına Kaydet
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO chat_history (session_id, user_message, bot_response)'
        ' VALUES (?, ?, ?)',
        (session_id, user_message, bot_response),
    )
    conn.commit()
    conn.close()

    return jsonify({'response': bot_response, 'model_used': chosen_model})

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
