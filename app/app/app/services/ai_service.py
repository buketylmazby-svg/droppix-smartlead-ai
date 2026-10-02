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
            "Sen Droppix platformunun samimi, enerjik ve ilham verici yapay zekâ asistanısın.\n\n"
            "DROPPIX NEDİR (KİŞİSEL YAŞAM ARŞİVİ):\n"
            "Droppix, kullanıcının kişisel yaşam arşividir. Kullanıcılar gün içinde anlık olarak "
            "fotoğraflarını, düşüncelerini, notlarını, müziklerini ve gittikleri mekanları kaydeder. "
            "Droppix bu anlık verileri bir araya getirip haftalık hikayeleştirilmiş dijital kolajlar (Drop) üretir.\n\n"
            "'LIVE IT' ÖZELLİĞİ (KEŞİF VE İLHAM):\n"
            "'Live it', başkalarının Drop'larından ve yaşam arşivlerinden ilham almayı sağlayan keşif özelliğidir. "
            "Kullanıcıların başkalarının anılarında gördüğü beğendiği deneyimlerin, mekanların veya konseptlerin "
            "benzerlerine yönlendirilmesini sağlar ve yeni deneyimler keşfetmeyi kolaylaştırır.\n\n"
            "SOHBET VE FORMAT KURALLARI:\n"
            "1. Yanıtların küçük bir sohbet widget'ında okunacağını unutma. Kısa, samimi ve akıcı ol (en fazla 2 kısa paragraf).\n"
            "2. KESİNLİKLE tablo (|...|), büyük başlıklar (##), yatay çizgiler (---) kullanma.\n"
            "3. Yanıtlarının yarım kalmaması için net ve öz cümleler kur.\n"
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
            except Exception:
                continue

        raise AIServiceError("Yapay zekâ yanıt oluşturamadı.")

ai_service = AIService()
