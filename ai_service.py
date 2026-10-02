import requests
from config import Config

class AIServiceError(Exception):
    """AI servisinde oluşan hatalar için özel istisna sınıfı."""
    pass

class AIService:
    def __init__(self):
        self.api_key = Config.GROQ_API_KEY
        self.model = "llama-3.1-8b-instant"
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"

    def yanit_uret(self, mesaj, gecmis=None):
        """
        Kullanıcı mesajını ve varsa geçmiş sohbeti alır, 
        Groq API üzerinden Droppix sistem yönergesiyle yanıt üretir.
        """
        if not self.api_key:
            return "Droppix Asistanı şu an demo modunda. Ekibimizin sizinle iletişime geçmesi için lütfen form doldurun!"

        if gecmis is None:
            gecmis = []

        # Sistem talimatını (BUSINESS_CONTEXT) en başa ekle
        messages = [
            {"role": "system", "content": Config.BUSINESS_CONTEXT}
        ]

        # Varsa geçmiş sohbetleri ekle
        for item in gecmis:
            messages.append(item)

        # Yeni kullanıcı mesajını ekle
        messages.append({"role": "user", "content": mesaj})

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7
        }

        try:
            response = requests.post(self.api_url, json=payload, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return data['choices'][0]['message']['content']
            else:
                print(f"Groq API Hatası ({response.status_code}): {response.text}")
                raise AIServiceError("Yapay zekâ yanıt oluşturamadı.")

        except requests.exceptions.RequestException as e:
            print(f"Bağlantı Hatası: {e}")
            raise AIServiceError("AI servisi ile bağlantı kurulamadı.")

# Kolay kullanım için tek bir örnek (instance) oluştur
ai_service = AIService()
