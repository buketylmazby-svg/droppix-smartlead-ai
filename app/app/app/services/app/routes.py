from flask import Blueprint, jsonify, request, render_template
from app.services.ai_service import ai_service
from app.database import db

main_bp = Blueprint('main', __name__)

@main_bp.route("/")
def home():
    return jsonify({"mesaj": "Droppix SmartLead AI Servisi Çalışıyor"}), 200

@main_bp.route("/health")
def health():
    return jsonify({"status": "healthy"}), 200

@main_bp.route("/api/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json() or {}
        mesaj = data.get("mesaj", "")
        
        if not mesaj:
            return jsonify({"basari": False, "hata": "Mesaj boş olamaz."}), 400

        yanit = ai_service.yanit_uret(mesaj)
        return jsonify({"basari": True, "cevap": yanit}), 200

    except Exception as e:
        return jsonify({"basari": False, "hata": str(e)}), 500

@main_bp.route("/api/lead", methods=["POST"])
def lead_ekle():
    try:
        data = request.get_json() or {}
        isim = data.get("isim")
        eposta = data.get("eposta")
        notlar = data.get("notlar", "")

        if not isim or not eposta:
            return jsonify({"basari": False, "hata": "İsim ve e-posta zorunludur."}), 400

        lead_id = db.lead_ekle(isim, eposta, notlar)
        return jsonify({"basari": True, "lead_id": lead_id}), 201
    except Exception as e:
        return jsonify({"basari": False, "hata": str(e)}), 500
