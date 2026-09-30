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
      return jsonify({
          'error': 'GROQ_API_KEY Render ortam değişkenlerinde bulunamadı.'
      }), 500

    # Denenecek güncel Groq modelleri sıralı listesi
    candidate_models = [
        'llama-3.3-70b-versatile',
        'llama-3.1-8b-instant',
        'mixtral-8x7b-32768',
        'gemma2-9b-it',
    ]

    bot_response = None
    last_error = None

    # Modelleri sırayla dener, çalışan ilk modelle yanıt üretir
    for model_name in candidate_models:
      try:
        completion = groq_client.chat.completions.create(
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
        break  # Başarılı olursa döngüden çık
      except Exception as err:
        last_error = str(err)
        continue

    if not bot_response:
      return (
          jsonify({
              'error': f'Hiçbir model yanıt vermedi. Son hata: {last_error}'
          }),
          500,
      )

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
