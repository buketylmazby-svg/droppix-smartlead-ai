import os
from groq import Groq

class AIServiceError(Exception):
    pass

class AIService:
    def __init__(self):
        # Groq üzerindeki en stabil modeller (biri çalışmazsa otomatik diğerine geçer)
        self.models = [
            "llama3-8b-8192",
            "llama3-70b-8192",
            "llama-3.3-70b-versatile",
            "mixtral-8x7b-32768"
        ]

    def yanit_uret(self, mesaj, gecmis=None):
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise AIServiceError("GROQ_API_KEY sistemde tanımlı değil.")

        client = Groq(api_key=api_key)

        system_prompt = (
            "Sen Droppix platformunun yapay zeka asistanısın. "
            "Kullanıcıların anılarını, fotoğraflarını, müziklerini ve düşüncelerini "
            "haftalık dijital kolajlar (Drop) halinde düzenleyen yaratıcı, samimi ve "
            "hikaye anlatıcısı bir tona sahipsin. Ayrıca kullanıcıların bu anıları canlı "
            "deneyimlemesini sağlayan 'Live it' özelliğini tanıtırsın."
        )

        messages = [{"role": "system", "content": system_prompt}]
        if gecmis:
            messages.extend(gecmis)
        messages.append({"role": "user", "content": mesaj})

        son_hata = None
        # Modelleri sırayla dener
        for model_name in self.models:
            try:
                completion = client.chat.completions.create(
                    model=model_name,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=500
                )
                return completion.choices[0].message.content
            except Exception as e:
                son_hata = str(e)
                print(f"Model {model_name} denenirken hata alındı, diğer modele geçiliyor: {son_hata}")
                continue

        raise AIServiceError(f"Yapay zekâ yanıt oluşturamadı. Detay: {son_hata}")

ai_service = AIService()
