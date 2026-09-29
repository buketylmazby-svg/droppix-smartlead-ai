from flask import Flask, request, jsonify
from flask_cors import CORS
from database import get_db_connection
from ai_service import get_ai_response

app = Flask(__name__)
# Farklı domainlerden (örn. Wix Velo, React) erişim için CORS izni
CORS(app)

@app.route('/', methods=['GET'])
def home():
    """Servisin aktifliğini denetleyen sağlık kontrolü (Health Check)."""
    return jsonify({
        "status": "online",
        "service": "Droppix SmartLead AI Backend",
        "version": "1.0.0"
    }), 200

@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Kullanıcı mesajını alır, veritabanından geçmişi okur, 
    Groq AI yanıtını üretir ve konuşmayı kaydeder.
    """
    data = request.get_json() or {}
    user_message = data.get('message')
    session_id = data.get('session_id', 'default_session')

    if not user_message:
        return jsonify({"error": "Mesaj alanı boş bırakılamaz."}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    # Kullanıcıya özel son 6 mesajlık konuşma geçmişini çek
    cursor.execute(
        "SELECT sender, message FROM chat_history WHERE session_id = ? ORDER BY timestamp ASC LIMIT 6",
        (session_id,)
    )
    raw_history = cursor.fetchall()
    chat_history = [{"sender": row["sender"], "message": row["message"]} for row in raw_history]

    # AI Yanıtını Üret
    ai_response = get_ai_response(user_message, chat_history)

    # Sohbeti Veritabanına İşle
    cursor.execute(
        "INSERT INTO chat_history (session_id, sender, message) VALUES (?, ?, ?)",
        (session_id, 'user', user_message)
    )
    cursor.execute(
        "INSERT INTO chat_history (session_id, sender, message) VALUES (?, ?, ?)",
        (session_id, 'assistant', ai_response)
    )
    conn.commit()
    conn.close()

    return jsonify({
        "status": "success",
        "session_id": session_id,
        "response": ai_response
    }), 200

@app.route('/api/lead', methods=['POST'])
def add_lead():
    """
    Potansiyel B2B partner veya B2C kullanıcının iletişim bilgilerini kaydeder.
    """
    data = request.get_json() or {}
    name = data.get('name')
    email = data.get('email')
    phone = data.get('phone', '')
    user_type = data.get('user_type', 'b2c')  # 'b2c' veya 'b2b'
    notes = data.get('notes', '')

    if not name or not email:
        return jsonify({"error": "İsim ve e-posta zorunludur."}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO leads (name, email, phone, user_type, notes) VALUES (?, ?, ?, ?, ?)",
        (name, email, phone, user_type, notes)
    )
    conn.commit()
    conn.close()

    return jsonify({
        "status": "success",
        "message": f"{user_type.upper()} kaydı başarıyla oluşturuldu!"
    }), 201

if __name__ == '__main__':
    # Lokal geliştirme sunucusu (Port 5000)
    app.run(debug=True, host='0.0.0.0', port=5000)