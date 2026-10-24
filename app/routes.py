from flask import Blueprint, jsonify, request, render_template
from app.services.ai_service import ai_service
from app.database import db

main_bp = Blueprint('main', __name__)

@main_bp.route("/")
def home():
    return render_template("index.html")

@main_bp.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

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

# Yeni kayıt ekle (Wix formu buraya gönderir)
@main_bp.route("/api/leads", methods=["POST"])
def lead_kaydet():
    try:
        data = request.get_json() or {}
        isim = (data.get("isim") or "").strip()
        telefon = (data.get("telefon") or "").strip()
        mesaj = (data.get("mesaj") or "").strip()

        if not isim or not telefon:
            return jsonify({"basari": False, "hata": "İsim ve telefon zorunlu."}), 400

        yeni_id = db.lead_ekle(isim, telefon, mesaj)
        return jsonify({"basari": True, "id": yeni_id}), 201
    except Exception as e:
        return jsonify({"basari": False, "hata": str(e)}), 500

# Tüm kayıtları listele (dashboard buradan okur)
@main_bp.route("/api/leads", methods=["GET"])
def lead_listele():
    try:
        return jsonify({"basari": True, "leads": db.tum_leadler()}), 200
    except Exception as e:
        return jsonify({"basari": False, "hata": str(e)}), 500