# Droppix — SmartLead AI (Akıllı Satış & Influencer Asistanı)

**Droppix SmartLead AI**, e-ticaret ve B2B platformları için geliştirilmiş yapay zekâ destekli akıllı müşteri ve influencer yakalama sistemidir. Sistem, web sitesine giren yeni kullanıcıları anında sıcak bir dille karşılar, yöneltilen soruları yanıtlar ve potansiyel müşteri ile iş birliği yapılabilecek influencer'ların iletişim bilgilerini toplayıp yönetim panelinde kategorize eder.

---

## 🚀 Öne Çıkan Özellikler

- **👋 Akıllı Karşılama (Welcome & Onboarding):** Web sitesini ziyaret eden yeni kullanıcıları anında otomatik mesajlarla karşılar ve etkileşimi başlatır.
- **🌟 Influencer Yakalama & Lead Yönetimi:** Markanızla iş birliği potansiyeli olan influencer'ları ve potansiyel müşterileri tespit ederek iletişim bilgilerini filtreleyip toplar.
- **🤖 Çoklu AI Sağlayıcı Desteği:** Groq (Varsayılan), Google Gemini ve OpenAI altyapıları arasında dinamik geçiş esnekliği.
- **🛡️ Parametrik SQL Güvenliği:** SQLite veritabanı işlemlerinde SQL Injection saldırılarına karşı `?` parametre kullanımı.
- **📊 Gelişmiş Yönetim Paneli:** Toplanan potansiyel müşterileri ve influencer kayıtlarını tarihe göre sıralı biçimde listeleme.
- **🌐 CORS & Entegrasyon Desteği:** Dış istemcilerden (Wix, Velo, mobil uygulamalar vb.) güvenli API erişimi.

---

## 🏗️ Proje Mimarisi (Separation of Concerns)

Bu proje, kodun okunabilirliğini ve bakımını kolaylaştırmak amacıyla katmanlı mimari prensiplerine uygun olarak geliştirilmiştir:

```text
droppix-smartlead-ai/
├── run.py                 # Sunucuyu başlatan giriş noktası (Application Entrypoint)
├── config.py              # Çevre değişkenleri ve uygulama konfigürasyonu
├── requirements.txt       # Python kütüphane bağımlılıkları
├── .gitignore             # Git izleme dışı dosyalar (.env vb.)
├── README.md              # Proje dokümantasyonu
└── app/
    ├── __init__.py        # Application Factory (create_app)
    ├── database.py        # Veritabanı (SQLite) CRUD işlemleri (SADECE burada)
    ├── routes.py          # HTTP Endpoint rotaları ve istek yönlendirme
    ├── templates/         # HTML Ön Yüz Dosyaları
    │   ├── index.html     # Ziyaretçi karşılama ve AI sohbet ekranı
    │   └── dashboard.html # Müşteri adayları ve Influencer yönetim paneli
    └── services/          # Dış Servis Entegrasyonları
        ├── __init__.py    # Services modül tanımı
        └── ai_service.py  # Yapay Zekâ (Groq / Gemini / OpenAI) API çağrıları
