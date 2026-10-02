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

        # Chatbot için özel olarak tanımlanmış Droppix ve Live it kuralları
        system_prompt = (
            "Sen Droppix platformunun samimi, enerjik ve yaratıcı yapay zekâ asistanısın. "
            "Droppix; kullanıcıların fotoğraflarını, müziklerini, notlarını ve düşüncelerini "
            "haftalık dijital kolajlar (Drop) hâlinde toplayan bir platformdur.\n\n"
            "ÖNEMLİ ÖZELLİK - 'Live it':\n"
            "'Live it', kullanıcının oluşturduğu Drop'lardaki anılarına, mekanlarına ve müziklerine "
            "dayanarak onlara yeni ve canlı interaktif aktivite/deneyim önerileri sunan akıllı öneri özelliğidir.\n\n"
            "SOHBET VE FORMAT KURALLARI:\n"
            "1. Yanıtların küçük bir sohbet penceresinde okunacağını unutma. Kısa, samimi ve akıcı ol (en fazla 2 kısa paragraf).\n"
            "2. KESİNLİKLE tablo (|...|), büyük başlıklar (##), yatay çizgiler (---) veya uzun liste formatları KULLANMA.\n"
            "3. Yanıtlarının yarım kalmaması için uzun açıklamalar yerine net cümleler kur.\n"
            "4. Doğal bir sohbet tonu kullan, tatlı birkaç emoji ekleyebilirsin."
        )

        messages = [{"role": "system", "content": system_prompt}]
        if gecmis:
            messages.extend(gecmis)
        messages.append({"role": "user", "content": mesaj})

        try:
            model_response = client.models.list()
            aktif_modeller = [
                m.id for m in model_response.data 
                if not any(k in m.id.lower() for k in ["whisper", "guard", "safeguard", "orpheus"])
            ]
        except Exception:
            aktif_modeller = ["llama-3.3-70b-versatile"]

        for model_name in aktif_modeller:
            try:
                completion = client.chat.completions.create(
                    model=model_name,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=350
                )
                return completion.choices[0].message.content
            except Exception as e:
                continue

        raise AIServiceError("Yapay zekâ yanıt oluşturamadı.")

ai_service = AIService()
