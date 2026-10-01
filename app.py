import os
import sqlite3
from flask import Flask, jsonify, request
from flask_cors import CORS
from groq import Groq

app = Flask(__name__)
CORS(app)


def init_db():
  try:
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
  except Exception as db_err:
    print(f'DB Init Hata: {db_err}')


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

    # 1. Groq hesabında ŞU AN aktif olan tüm modelleri çek
    active_model_ids = []
    try:
      models_page = client.models.list()
      active_model_ids = [m.id for m in models_page.data]
    except Exception as api_err:
      print(f'Model listesi çekilemedi: {api_err}')

    # 2. Tercih edilen öncelikli Türkçe modeller
    preferred_candidates = [
        'llama-3.3-70b-versatile',
        'llama3-70b-8192',
        'llama3-8b-8192',
        'gemma2-9b-it',
    ]

    # Sadece Groq'ta ŞU AN GERÇEKTEN VAR OLAN modelleri listeye al
    candidate_models = [
        m for m in preferred_candidates if m in active_model_ids
    ]

    # Eğer tercih edilenler listede yoksa, aktif modellerden sohbet dışı olanları süzerek yedek oluştur
    if not candidate_models:
      ignored_keywords = [
          'guard',
          'whisper',
          'embed',
          'classifier',
          'moderation',
          'orpheus',
          'vision',
          'allam',
          'speech',
      ]
      candidate_models = [
          m
          for m in active_model_ids
          if not any(ik in m.lower() for ik in ignored_keywords)
      ]

    # Son çare güvenlik yedeği
    if not candidate_models:
      candidate_models = ['llama-3.3-70b-versatile']

    # 3. Sistem Yönergesi
    system_prompt = (
        "Sen Droppix AI'sin, Droppix platformunun akıllı asistanısın. "
        "YALNIZCA Türkçe yanıt ver. Kendini tanıtırken 'Droppix'in akıllı"
        ' asistanıyım\' ifadesini kullan. Kullanıcı işbirliği, iletişim veya'
        ' hizmet almak istediğinde nazikçe memnuniyetini belirt ve size'
        ' ulaşabilmemiz için adını ve iletişim bilgilerini (e-posta veya'
        ' telefon) paylaşmasını rica et.'
    )

    bot_response = None
    used_model = None
    last_error = ''

    # Doğrulanmış modelleri sırayla dene
    for model_id in candidate_models:
      try:
        completion = client.chat.completions.create(
            model=model_id,
            temperature=0.6,
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_message},
            ],
        )
        bot_response = completion.choices[0].message.content
        if bot_response:
          used_model = model_id
          break
      except Exception as err:
        last_error = str(err)
        continue

    if not bot_response:
      return (
          jsonify({
              'error': (
                  'Sohbet modeli yanıt veremedi. Lütfen tekrar deneyin. Detay:'
                  f' {last_error}'
              )
          }),
          500,
      )

    # 4. Veritabanına Kaydet
    try:
      conn = sqlite3.connect('database.db')
      cursor = conn.cursor()
      cursor.execute(
          'INSERT INTO chat_history (session_id, user_message, bot_response)'
          ' VALUES (?, ?, ?)',
          (session_id, user_message, bot_response),
      )
      conn.commit()
      conn.close()
    except Exception as db_save_err:
      print(f'Sohbet veritabanına kaydedilemedi: {db_save_err}')

    return jsonify({'response': bot_response, 'model_used': used_model})

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
