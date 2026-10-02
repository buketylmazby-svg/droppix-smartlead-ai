import os
from groq import Groq

class AIServiceError(Exception):
    pass

class AIService:
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

        # Groq hesabında o an aktif ve erişilebilir olan modelleri dinamik sorgula
        try:
            model_response = client.models.list()
            # Ses (whisper) ve güvenlik (guard) dışındaki sohbet modellerini seç
            aktif_modeller = [
                m.id for m in model_response.data 
                if not any(k in m.id.lower() for k in ["whisper", "guard", "safeguard", "orpheus"])
            ]
        except Exception as e:
            # Sorgu çalışmazsa yedek varsayılan liste
            aktif_modeller = ["llama-3.1-8b-instant", "llama-3.3-70b-versatile"]

        hatalar = []
        for model_name in aktif_modeller:
            try:
                completion = client.chat.completions.create(
                    model=model_name,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=500
                )
                return completion.choices[0].message.content
            except Exception as e:
                hata_detayi = f"{model_name}: {str(e)}"
                hatalar.append(hata_detayi)
                print(f"Model deneme hatası -> {hata_detayi}")
                continue

        raise AIServiceError(f"Yapay zekâ yanıt oluşturamadı. Denenen Modeller: {aktif_modeller}. Detay: {' | '.join(hatalar)}")

ai_service = AIService()
