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

    # 1. Groq hesabında ŞU AN aktif olan tüm modelleri doğrula
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

    candidate_models = [
        m for m in preferred_candidates if m in active_model_ids
    ]

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

    if not candidate_models:
      candidate_models = ['llama-3.3-70b-versatile']

    # 3. Özel Droppix Sistem Yönergesi
    system_prompt = (
        "Sen Droppix AI'sin, Droppix platformunun resmi akıllı asistanısın.\n"
        "YALNIZCA Türkçe yanıt ver.\n\n"
        "DROPPİX PLATFORM TANIMI VE ANA MESAJI:\n"
        "Kullanıcı Droppix'in ne olduğunu, nasıl çalıştığını sorduğunda veya"
        " genel bilgi istediğinde aşağıdaki mesaj yapısını ve samimi tonu esas"
        " alarak yanıt ver:\n\n"
        "\"Merhaba! Ben Droppix'in akıllı asistanıyım.\n"
        "Droppix; yaşamındaki her şeyi tek bir yerde zahmetsizce arşivlemene"
        " olanak tanıyan bir yaşam alanıdır. Fotoğraflarını, gün içinde"
        " dinlediğin şarkıları, unutmak istemediğin notları, gezip gördüğün"
        " mekanları ve aklına gelebilecek tüm anıları tek bir yerde biriktirmek"
        " burada çok kolay.\n"
        "Üstelik biriktirdiğin tüm bu değerli anlar, periyodik aralıklarla sana"
        " hikayeleştirilmiş estetik birer kolaj—yani 'drop'—olarak geri dönüyor."
        " 'Live it' özelliği sayesinde ise sadece geçmişini saklamakla kalmıyor,"
        " başkalarından aldığın ilhamı kendi yaşamına uyarlamanı sağlayacak"
        " kişisel öneriler keşfedebiliyorsun.\n"
        "Sana Droppix dünyası hakkında detaylı bilgi vermemi veya ekibimizin"
        " seninle iletişime geçmesini ister misin?\"\n\n"
        "KURALLAR:\n"
        "1. Yanıtlarında asla soğuk madde işaretleri (1., 2., -) kullanma."
        " Hikaye anlatan, ilham verici ve akıcı bir dil benimse.\n"
        "2. Kullanıcı iş birliği kurmak, iletişim sağlamak veya ekiple"
        " görüşmek istediğinde memnuniyetini belirtip adını ve iletişim"
        " bilgisini (e-posta veya telefon numarası) paylaşmasını rica et."
    )

    bot_response = None
    used_model = None
    last_error = ''

    for model_id in candidate_models:
      try:
        completion = client.chat.completions.create(
            model=model_id,
            temperature=0.5,
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
