# 🚀 Droppix SmartLead AI Backend

Droppix platformu için geliştirilmiş; yapay zeka destekli sohbet (chat) ve potansiyel müşteri (lead) toplama altyapısı sunan Flask tabanlı RESTful API servisi.

## 🛠️ Teknolojiler ve Mimari

* **Backend Framework:** Python / Flask
* **AI Engine:** Groq API (`llama-3.3-70b-versatile` öncelikli model yedekleme/fallback mimarisi)
* **Veritabanı:** SQLite3 (`chat_history` ve `leads` tabloları)
* **Güvenlik & Erişim:** Flask-CORS (Wix Velo ve harici frontend entegrasyonu için)
* **Deployment:** Render PaaS

---

## 🔌 API Uç Noktaları (Endpoints)

### 1. Sistem Durumu
* **Endpoint:** `GET /`
* **Açıklama:** Servisin canlıda ve aktif olup olmadığını kontrol eder.

### 2. Yapay Zeka Sohbeti
* **Endpoint:** `POST /api/chat`
* **Request Body:**
  ```json
  {
    "message": "Merhaba, Droppix nedir?",
    "session_id": "user_123"
  }
