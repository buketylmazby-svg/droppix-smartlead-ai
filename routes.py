from flask import Blueprint, request, jsonify
from database import lead_ekle, tum_leadler
from ai_service import ai_service, AIServiceError

# Blueprint tanımı
main_bp = Blueprint('main', __name__)

@main_bp.route('/health', methods=['GET'])
def health_check():
    """Sunucunun canlılık kontrol noktası."""
    return jsonify({"basari": True, "durum": "aktif", "mesaj": "Droppix Backend Calisiyor"}), 200

@main_bp.route('/api/sohbet', methods=['POST'])
@main_bp.route('/api/chat', methods=['POST'])
def sohbet():
    """Yapay zeka ile sohbet uç noktası."""
    try:
        data = request.get_json() or {}
        mesaj = data.get('mesaj') or data.get('message')
        gecmis = data.get('gecmis', [])

        if not mesaj:
            return jsonify({"basari": False, "hata": "Mesaj alanı boş olamaz"}), 400

        yanit = ai_service.yanit_uret(mesaj, gecmis)
        return jsonify({"basari": True, "cevap": yanit, "reply": yanit}), 200

    except AIServiceError as e:
        return jsonify({"basari": False, "hata": str(e)}), 503
    except Exception as e:
        return jsonify({"basari": False, "hata": "Sunucu içi bir hata oluştu"}), 500

@main_bp.route('/api/leads', methods=['POST'])
@main_bp.route('/api/lead', methods=['POST'])
def lead_kaydet():
    """Yeni müşteri adayı kaydetme uç noktası."""
    try:
        data = request.get_json() or {}
        isim = data.get('isim') or data.get('name')
        telefon = data.get('telefon') or data.get('phone')
        mesaj = data.get('mesaj', '')

        if not isim or not telefon:
            return jsonify({"basari": False, "hata": "İsim ve telefon zorunludur"}), 400

        sonuc = lead_ekle(isim, telefon, mesaj)
        if sonuc:
            return jsonify({"basari": True, "mesaj": "Kayıt başarıyla oluşturuldu"}), 201
        else:
            return jsonify({"basari": False, "hata": "Veritabanına kaydedilemedi"}), 500

    except Exception as e:
        return jsonify({"basari": False, "hata": str(e)}), 500

@main_bp.route('/api/leads', methods=['GET'])
def lead_listele():
    """Yönetim paneli için tüm kayıtları getiren uç nokta."""
    try:
        kayitlar = tum_leadler()
        return jsonify({"basari": True, "data": kayitlar, "leads": kayitlar}), 200
    except Exception as e:
        return jsonify({"basari": False, "hata": str(e)}), 500
