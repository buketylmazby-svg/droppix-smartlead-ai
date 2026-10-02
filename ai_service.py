import os
from groq import Groq

class AIServiceError(Exception):
    pass

class AIService:
    def __init__(self):
        # Groq üzerinde şu an aktif olan güncel modeller
        self.models = [
            "llama-3.3-70b-versatile",
            "gemma2-9b-it",
            "llama-3.2-3b-preview"
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

        hatalar = []
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
                hata_msg = f"{model_name}: {str(e)}"
                hatalar.append(hata_msg)
                print(f"Model deneme hatası -> {hata_msg}")
                continue

        raise AIServiceError(f"Yapay zekâ yanıt oluşturamadı. Detay: {' | '.join(hatalar)}")

ai_service = AIService()
