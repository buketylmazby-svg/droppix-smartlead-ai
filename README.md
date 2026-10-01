# 🚀 Droppix SmartLead AI Backend

Droppix platformu için geliştirilmiş; yapay zeka destekli sohbet (chat) ve potansiyel müşteri (lead) toplama altyapısı sunan Flask tabanlı RESTful API servisi.

## 🛠️ Teknolojiler ve Mimari

* **Backend Framework:** Python / Flask
* **AI Engine:** Groq API (`llama-3.3-70b-versatile` öncelikli model yedekleme mimarisi)
* **Veritabanı:** SQLite3 (`chat_history` ve `leads` tabloları)
* **Güvenlik & Erişim:** Flask-CORS (Wix Velo entegrasyonu için)
* **Deployment:** Render PaaS

---

## 🔌 API Uç Noktaları (Endpoints)

### 1. Sistem Durumu
* **Endpoint:** `GET /`
* **Açıklama:** Servisin canlıda ve aktif olup olmadığını kontrol eder.

### 2. Yapay Zeka Sohbeti
* **Endpoint:** `POST /api/chat`
* **Gönderilen Veri (Request Body):**
  - `message`: Kullanıcının attığı mesaj
  - `session_id`: Oturum kimliği

* **Dönen Yanıt (Response):**
  - `response`: Yapay zekanın verdiği cevap
  - `model_used`: Cevabı üreten aktif model ismi

### 3. Müşteri Adayı Kaydı (Lead Generation)
* **Endpoint:** `POST /api/lead`
* **Gönderilen Veri (Request Body):**
  - `name`: Müşterinin adı
  - `contact`: E-posta veya telefon numarası
  - `notes`: Ek Notlar

---

## ⚙️ Yerel Kurulum ve Çalıştırma

1. Depoyu klonlayın:
   `git clone <repo-url>`
   `cd <repo-klasoru>`

2. Gerekli kütüphaneleri yükleyin:
   `pip install -r requirements.txt`

3. Ortam değişkenini tanımlayıp uygulamayı başlatın:
   `export GROQ_API_KEY="groq-api-anahtariniz"`
   `python app.py`

---

## 🌐 Render Canlı Ortam Kurulumu

1. Render üzerinde yeni bir **Web Service** oluşturun ve bu depoyu bağlayın.
2. **Environment Variables** sekmesinde `GROQ_API_KEY` anahtarını tanımlayın.
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `gunicorn app:app` veya `python app.py`
